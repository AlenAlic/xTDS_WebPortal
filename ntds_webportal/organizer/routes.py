from flask import render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from ntds_webportal import db
from ntds_webportal.main.email import send_new_messages_email
from ntds_webportal.organizer import bp
from ntds_webportal.models import requires_access_level, Team, TeamFinances, Contestant, ContestantInfo, DancingInfo,\
    StatusInfo, AdditionalInfo, NameChangeRequest, User, Notification, MerchandiseInfo, Merchandise, TournamentState, \
    SalsaPartners, PolkaPartners, VolunteerInfo
from ntds_webportal.functions import uniquify, check_combination, get_combinations_list
from ntds_webportal.organizer.forms import NameChangeResponse
from ntds_webportal.organizer.email import send_raffle_completed_email
import ntds_webportal.data as data
from ntds_webportal.data import *
from raffle_system.system import raffle, finish_raffle, raffle_add_neutral_group, test_raffle
from raffle_system.functions import RaffleSystem, get_combinations, has_partners
from sqlalchemy import or_, case
import time
import random
import xlsxwriter
from io import BytesIO, StringIO
import datetime


@bp.route('/registration_overview', methods=['GET'])
@login_required
@requires_access_level([ACCESS['organizer']])
def registration_overview():
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .order_by(ContestantInfo.team_id,
                  case({CONFIRMED: 0, SELECTED: 1, REGISTERED: 2, CANCELLED: 3}, value=StatusInfo.status),
                  ContestantInfo.number).all()
    all_teams = db.session.query(Team).all()
    dancers = [{'country': team.country, 'name': team.name, 'id': team.name.replace(' ', '-').replace('`', ''),
                'dancers': db.session.query(Contestant).join(ContestantInfo).filter(ContestantInfo.team == team).all()}
               for team in all_teams]
    # dancers = [d for d in dancers if len(d['dancers']) > 0]
    dutch_dancers = [team for team in dancers if team['country'] == NETHERLANDS]
    german_dancers = [team for team in dancers if team['country'] == GERMANY]
    other_dancers = [team for team in dancers if team['country'] != NETHERLANDS and
                     team['country'] != GERMANY]
    return render_template('organizer/registration_overview.html', data=data, all_dancers=all_dancers,
                           dutch_dancers=dutch_dancers, german_dancers=german_dancers, other_dancers=other_dancers)


@bp.route('/finances_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['organizer']])
def finances_overview():
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .filter(StatusInfo.payment_required.is_(True)).order_by(ContestantInfo.team_id, ContestantInfo.number).all()
    all_confirmed_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.payment_required.is_(True), StatusInfo.status == CONFIRMED)\
        .order_by(ContestantInfo.team_id, ContestantInfo.number).all()
    all_cancelled_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.payment_required.is_(True), StatusInfo.status == CANCELLED) \
        .order_by(ContestantInfo.team_id, ContestantInfo.number).all()
    all_teams = db.session.query(Team).join(TeamFinances).all()
    teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
              'confirmed_dancers': [dancer for dancer in all_confirmed_dancers if
                                    dancer.contestant_info[0].team.name == team.name],
              'cancelled_dancers': [dancer for dancer in all_cancelled_dancers if
                                    dancer.contestant_info[0].team.name == team.name],
              'finances': data.finances_overview([dancer for dancer in all_dancers if
                                                  dancer.contestant_info[0].team.name == team.name])}
             for team in all_teams]
    teams = [team for team in teams if (len(team['confirmed_dancers']) + len(team['cancelled_dancers'])) > 0]
    dutch_teams = [team for team in teams if team['team'].country == NETHERLANDS]
    german_teams = [team for team in teams if team['team'].country == GERMANY]
    other_teams = [team for team in teams if
                   team['team'].country != NETHERLANDS and team['team'].country != GERMANY]
    if request.method == 'POST':
        if 'submit' in request.form:
            changes = False
            for team in all_teams:
                amount_paid = request.form.get(str(team.team_id))
                if amount_paid != '' and amount_paid is not None:
                    amount_paid = int(float(amount_paid)*100)
                    if team.finances[0].paid != amount_paid:
                        team.finances[0].paid = amount_paid
                        changes = True
            if changes:
                db.session.commit()
                flash('Changes saved successfully.', 'alert-success')
            else:
                flash('No changes were made to submit.', 'alert-warning')
            return redirect(url_for('organizer.finances_overview'))
    return render_template('organizer/finances_overview.html', teams=teams, data=data,
                           dutch_teams=dutch_teams, german_teams=german_teams, other_teams=other_teams)


@bp.route('/remove_payment_requirement/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['organizer']])
def remove_payment_requirement(number):
    dancer = StatusInfo.query.filter(StatusInfo.contestant_id == number).first()
    dancer.payment_required = False
    db.session.commit()
    return redirect(url_for('organizer.finances_overview'))


@bp.route('/name_change_list', methods=['GET'])
@login_required
@requires_access_level([ACCESS['organizer']])
def name_change_list():
    nml = NameChangeRequest.query.filter_by(state=NameChangeRequest.STATE['Open']).all()
    return render_template('organizer/name_change_list.html', list=nml)


@bp.route('/name_change_respond/<req>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['organizer']])
def name_change_respond(req):
    req = NameChangeRequest.query.filter_by(id=req).first()
    if not req:
        return redirect('error.404')
    form = NameChangeResponse()
    if form.validate_on_submit():
        accepted = form.accept.data
        req.response = form.remark.data
        if accepted:
            flash('Name change request accepted')
            req.accept()
        else:
            flash('Name change request rejected')
            req.reject()
        db.session.commit()
        return redirect(url_for('organizer.name_change_list'))
    return render_template('organizer/name_change_respond.html', req=req, form=form)


@bp.route('/raffle_system', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['organizer']])
def raffle_system():
    raffle_sys = RaffleSystem()
    state = raffle_sys.state
    raffle_config = raffle_sys.raffle_config
    tournament_config = raffle_sys.tournament_config
    selected_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.raffle_status == SELECTED) \
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    confirmed_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.raffle_status == CONFIRMED) \
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    available_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.raffle_status == REGISTERED) \
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    first_time_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.raffle_status == REGISTERED, ContestantInfo.first_time.is_(True)) \
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    newly_selected, sleeping_spots = None, None
    stats_registered, stats_selected, stats_confirmed = None, None, None
    teams, available_combinations = None, None
    if request.method == 'GET':
        stats_registered = raffle_sys.get_stats(REGISTERED)
        if state.main_raffle_taken_place:
            stats_selected = raffle_sys.get_stats(SELECTED)
            stats_confirmed = raffle_sys.get_stats(CONFIRMED)

        combination_dancers = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
            .filter(StatusInfo.raffle_status == REGISTERED, DancingInfo.partner.is_(None)) \
            .order_by(ContestantInfo.team_id, Contestant.first_name).all()
        combination_dancers = [d for d in combination_dancers if has_partners(d) is False]
        available_combinations_list = [get_combinations(d) for d in combination_dancers]
        available_combinations = {comb: 0 for comb in uniquify(available_combinations_list)}
        for comb in available_combinations_list:
            available_combinations[comb] += 1

        all_teams = db.session.query(Team).all()
        teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
                  'id_title': team.name.replace(' ', '-').replace('`', '') + '-title',
                  'teamcaptains_selected': len(Contestant.query.join(ContestantInfo)
                                               .filter(ContestantInfo.team == team,
                                                       ContestantInfo.team_captain.is_(True)).all())}
                 for team in all_teams]
        if not state.main_raffle_taken_place:
            for t in teams:
                t['guaranteed_dancers'] = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
                    .filter(ContestantInfo.team == t['team'], StatusInfo.raffle_status != CANCELLED,
                            StatusInfo.guaranteed_entry.is_(True)).order_by(Contestant.first_name).all()
                t['available_dancers'] = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
                    .filter(ContestantInfo.team == t['team'], StatusInfo.raffle_status == REGISTERED) \
                    .order_by(Contestant.first_name).all()
        if state.main_raffle_taken_place and not state.main_raffle_result_visible:
            for t in teams:
                t['available_dancers'] = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
                    .filter(ContestantInfo.team == t['team'], StatusInfo.raffle_status == REGISTERED) \
                    .order_by(Contestant.first_name).all()
                t['selected_dancers'] = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
                    .filter(ContestantInfo.team == t['team'], StatusInfo.raffle_status == SELECTED)\
                    .order_by(Contestant.first_name).all()
            sleeping_spots = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo).join(AdditionalInfo) \
                .filter(or_(StatusInfo.raffle_status == SELECTED, StatusInfo.raffle_status == CONFIRMED),
                        AdditionalInfo.sleeping_arrangements.is_(True)).count()
        if state.main_raffle_taken_place and state.main_raffle_result_visible:
            for t in teams:
                t['available_dancers'] = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
                    .filter(ContestantInfo.team == t['team'], StatusInfo.raffle_status == REGISTERED).all()
                t['selected_dancers'] = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
                    .filter(ContestantInfo.team == t['team'], StatusInfo.raffle_status == SELECTED).all()
                t['confirmed_dancers'] = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
                    .filter(ContestantInfo.team == t['team'], StatusInfo.raffle_status == CONFIRMED).all()
            newly_selected = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
                .filter(StatusInfo.raffle_status == SELECTED, StatusInfo.status == REGISTERED)\
                .order_by(ContestantInfo.number).all()
            sleeping_spots = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo).join(AdditionalInfo) \
                .filter(or_(StatusInfo.raffle_status == SELECTED, StatusInfo.raffle_status == CONFIRMED),
                        AdditionalInfo.sleeping_arrangements.is_(True)).count()

    if request.method == 'POST':
        all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(StatusInfo.status != CANCELLED).order_by(ContestantInfo.team_id, Contestant.first_name).all()
        form = request.form
        if 'raffle_config' in form:
            for k, v in form.items():
                if k in raffle_config:
                    raffle_config[k] = v
            state.set_raffle_config(raffle_config)
        elif 'start_raffle' in form:
            guaranteed_dancers = [d for d in all_dancers if str(d.contestant_id) in form]
            for dancer in all_dancers:
                if dancer in guaranteed_dancers:
                    dancer.status_info[0].guaranteed_entry = True
                else:
                    dancer.status_info[0].guaranteed_entry = False
            raffle(raffle_sys, guaranteed_dancers=guaranteed_dancers)
            state.main_raffle_taken_place = True
            flash('Raffle completed.', 'alert-info')
        elif 'cancel_raffle' in form:
            for dancer in all_dancers:
                dancer.status_info[0].set_status(REGISTERED)
            state.main_raffle_taken_place = False
            flash('Raffle cancelled.', 'alert-info')
        elif 'confirm_raffle' in form:
            for dancer in selected_dancers:
                dancer.status_info[0].set_status(SELECTED)
            state.main_raffle_result_visible = True
            flash('Raffle confirmed. The results are now visible to the teamcaptains.', 'alert-success')
        elif 'reset_raffle' in form:
            for dancer in all_dancers:
                dancer.status_info[0].set_status(REGISTERED)
            state.main_raffle_taken_place = False
            state.main_raffle_result_visible = False
            state.raffle_completed_message_sent = False
            flash('Raffle results cleared.', 'alert-info')
        elif 'send_raffle_completed_message' in form:
            teamcaptains = User.query.filter(User.is_active, User.access == ACCESS['team_captain']).all()
            for tc in teamcaptains:
                dancers = Contestant.query.join(ContestantInfo).filter(ContestantInfo.team == tc.team).all()
                if len(dancers) > 0:
                    send_raffle_completed_email(tc.email)
            state.raffle_completed_message_sent = True
        elif 'do_not_send_raffle_completed_message' in form:
            state.raffle_completed_message_sent = True
        elif 'finish_raffle' in form:
            finish_raffle(raffle_sys)
        elif 'select_random_group' in form:
            flash(raffle_add_neutral_group(raffle_sys))
        elif 'select_marked_dancers' in form:
            marked_dancers = [d for d in all_dancers if str(d.contestant_id) in form]
            for dancer in marked_dancers:
                dancer.status_info[0].set_status(SELECTED)
                teamcaptain = User.query.filter(User.is_active, User.access == ACCESS['team_captain'],
                                                User.team == dancer.contestant_info[0].team).first()
                if teamcaptain.send_new_messages_email:
                    text = f"{dancer.get_full_name()} has been selected for the tournament by the raffle system.\n"
                    n = Notification(title=f"Selected {dancer.get_full_name()} for the tournament", text=text,
                                     user=teamcaptain)
                    db.session.add(n)
                    send_new_messages_email(current_user, teamcaptain)
        elif 'remove_marked_dancers' in form:
            marked_dancers = [d for d in all_dancers if str(d.contestant_id) in form]
            for dancer in marked_dancers:
                dancer.status_info[0].set_status(REGISTERED)
        elif 'start_test_raffle' in form:
            runs = 25
            guaranteed_dancers = [d for d in all_dancers if str(d.contestant_id) in form]
            if True:
                start_time = time.time()
                for i in range(0, runs):
                    print(f'Performing run {i+1} of {runs}...')
                    test_raffle(guaranteed_dancers)
                print(f"--- {runs} raffles done in %.3f seconds ---" % (time.time() - start_time))
            else:
                test_raffle(guaranteed_dancers)
        else:
            if not raffle_sys.full():
                try:
                    s = [f for f in form][0]
                except IndexError:
                    pass
                else:
                    s = get_combinations_list(s)
                    single_dancers = [d for d in available_dancers if check_combination(d, s)]
                    single_dancers = [d for d in single_dancers if has_partners(d) is False]
                    try:
                        single_dancer = random.choice(single_dancers)
                        single_dancer.status_info[0].raffle_status = SELECTED
                        flash('Selected {}.'.format(single_dancer.get_full_name()))
                    except IndexError:
                        pass
            else:
                flash('You cannot add more dancers.', 'alert-warning')
        db.session.commit()
        return redirect(url_for('organizer.raffle_system'))
    return render_template('organizer/raffle_system.html', state=state, data=data, raffle_sys=raffle_sys,
                           tournament_config=tournament_config, raffle_config=raffle_config, teams=teams,
                           stats_registered=stats_registered, stats_selected=stats_selected,
                           stats_confirmed=stats_confirmed, selected_dancers=selected_dancers,
                           confirmed_dancers=confirmed_dancers, available_dancers=available_dancers,
                           available_combinations=available_combinations, newly_selected=newly_selected,
                           sleeping_spots=sleeping_spots, first_time_dancers=first_time_dancers)


@bp.route('/cancel_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['organizer']])
def cancel_dancer(number):
    send_message = request.args.get('send_message', False, type=bool)
    changed_dancer = db.session.query(Contestant).join(ContestantInfo)\
        .filter(Contestant.contestant_id == number).first()
    changed_dancer.cancel_registration()
    db.session.commit()
    flash('The registration of {} has been cancelled.'.format(changed_dancer.get_full_name()), 'alert-info')
    if send_message:
        text = f"{changed_dancer.get_full_name()}' registration has been cancelled by the organization.\n"
        n = Notification(title=f"Cancelled registration of {changed_dancer.get_full_name()}", text=text,
                         user=User.query.filter(User.access == ACCESS['team_captain'],
                                                User.team == changed_dancer.contestant_info[0].team).first())
        db.session.add(n)
        db.session.commit()
    return redirect(url_for('organizer.raffle_system'))


@bp.route('/merchandise', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['organizer']])
def merchandise():
    ts = TournamentState.query.first()
    dancers = Contestant.query.join(StatusInfo).join(ContestantInfo).join(AdditionalInfo).join(MerchandiseInfo)\
        .join(Team).filter(or_(StatusInfo.status == CONFIRMED, StatusInfo.status == CANCELLED),
                           or_(MerchandiseInfo.quantity > 0, AdditionalInfo.t_shirt != NO)).order_by(Team.city).all()
    shirts = {code: 0 for code in SHIRT_SIZES}
    for dancer in dancers:
        try:
            shirts[dancer.additional_info[0].t_shirt] += 1
        except KeyError:
            pass
    shirts = {SHIRT_SIZES[shirt]: quantity for shirt, quantity in shirts.items()}
    total_shirts = sum([quantity for size, quantity in shirts.items()])
    all_stickers = Merchandise.query.all()
    ordered_stickers = []
    for dancer in dancers:
        ordered_stickers.extend(dancer.merchandise_info)
    stickers = {sticker.merchandise_id: 0 for sticker in all_stickers}
    for sticker in ordered_stickers:
        stickers[sticker.product_id] += sticker.quantity
    stickers = {sticker.product_description: stickers[sticker.merchandise_id] for sticker in all_stickers}
    total_stickers = sum([quantity for sticker, quantity in stickers.items()])
    form = request.args
    if 'download_file' in form:
        fn = 'merchandise_ETDS_2018.xlsx'
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        f = wb.add_format({'text_wrap': True, 'bold': True})
        ws = wb.add_worksheet(name=datetime.date.today().strftime("%B %d, %Y"))
        ws.write(0, 0, 'Dancer', f)
        ws.write(0, 1, 'Email', f)
        ws.write(0, 2, 'Team', f)
        ws.write(0, 3, 'T-shirt', f)
        ws.set_column(0, 0, 30)
        ws.set_column(1, 1, 40)
        ws.set_column(2, 3, 20)
        for s in range(0, len(all_stickers)):
            ws.write(0, s + 4, all_stickers[s].product_description, f)
        for d in range(0, len(dancers)):
            ws.write(d + 1, 0, dancers[d].get_full_name())
            ws.write(d + 1, 1, dancers[d].email)
            ws.write(d + 1, 2, dancers[d].contestant_info[0].team.city)
            try:
                ws.write(d + 1, 3, SHIRT_SIZES[dancers[d].additional_info[0].t_shirt])
            except KeyError:
                ws.write(d + 1, 3, NONE)
            for m in range(0, len(dancers[d].merchandise_info)):
                ws.write(d + 1, m + 4, dancers[d].merchandise_info[m].quantity)
        ws.set_column(4, 4 + len(all_stickers), 13)
        ws.freeze_panes(1, 0)
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename=fn)
    return render_template('organizer/merchandise.html', ts=ts, data=data, shirts=shirts, total_shirts=total_shirts,
                           stickers=stickers, total_stickers=total_stickers, dancers=dancers)


@bp.route('/BAD', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['organizer']])
def bad():
    ts = TournamentState.query.first()
    form = request.args
    if 'download_createUniverse' in form:
        output = StringIO(render_template('organizer/_BAD_createUniverse.sql'))
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="createUniverse.sql")
    if 'download_createDB' in form:
        output = StringIO(render_template('organizer/_BAD_createDB.sql'))
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="createDB.sql")
    if 'download_createTournament' in form:
        teams = Team.query.all()
        dancers = Contestant.query.join(StatusInfo)\
            .filter(or_(StatusInfo.status == SELECTED, StatusInfo.status == CONFIRMED)).all()
        text = render_template('organizer/_BAD_createTournament.sql', teams=teams, dancers=dancers)
        output = StringIO(text)
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="createTournament.sql")
    if 'download_populateCouples' in form:
        leads = Contestant.query.join(StatusInfo).join(DancingInfo) \
            .filter(or_(StatusInfo.status == SELECTED, StatusInfo.status == CONFIRMED), DancingInfo.role == LEAD) \
            .all()
        leads = [di for lead in leads for di in lead.dancing_info if di.role == LEAD and di.partner is not None]
        salsa_couples = SalsaPartners.query.all()
        polka_couples = PolkaPartners.query.all()
        text = render_template('organizer/_BAD_populateCouples.sql', leads=leads,
                               salsa_couples=salsa_couples, polka_couples=polka_couples)
        output = StringIO(text)
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="populateCouples.sql")
    return render_template('organizer/BAD.html', ts=ts)


@bp.route('/adjudicators_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['organizer']])
def adjudicators_overview():
    ts = TournamentState.query.first()
    ballroom_adjudicators = Contestant.query.join(VolunteerInfo, StatusInfo, ContestantInfo)\
        .filter(StatusInfo.status == CONFIRMED, VolunteerInfo.jury_ballroom != NO)\
        .order_by(case({YES: 0, MAYBE: 1, NO: 2}, value=VolunteerInfo.jury_ballroom), ContestantInfo.team_id)\
        .all()
    latin_adjudicators = Contestant.query.join(VolunteerInfo, StatusInfo, ContestantInfo) \
        .filter(StatusInfo.status == CONFIRMED, VolunteerInfo.jury_latin != NO) \
        .order_by(case({YES: 0, MAYBE: 1, NO: 2}, value=VolunteerInfo.jury_latin), ContestantInfo.team_id) \
        .all()
    salsa_adjudicators = Contestant.query.join(VolunteerInfo, StatusInfo, ContestantInfo) \
        .filter(StatusInfo.status == CONFIRMED, VolunteerInfo.jury_salsa != NO) \
        .order_by(case({YES: 0, MAYBE: 1, NO: 2}, value=VolunteerInfo.jury_salsa), ContestantInfo.team_id) \
        .all()
    polka_adjudicators = Contestant.query.join(VolunteerInfo, StatusInfo, ContestantInfo) \
        .filter(StatusInfo.status == CONFIRMED, VolunteerInfo.jury_polka != NO) \
        .order_by(case({YES: 0, MAYBE: 1, NO: 2}, value=VolunteerInfo.jury_polka), ContestantInfo.team_id) \
        .all()
    form = request.args
    if 'download_file' in form:
        fn = 'adjudicators_ETDS_2018.xlsx'
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        f = wb.add_format({'text_wrap': True, 'bold': True})
        adjudicators = {BALLROOM: ballroom_adjudicators, LATIN: latin_adjudicators, SALSA: salsa_adjudicators,
                        POLKA: polka_adjudicators}
        for comp, adj in adjudicators.items():
            ws = wb.add_worksheet(name=comp)
            ws.write(0, 0, 'Dancer', f)
            ws.write(0, 1, 'Team', f)
            ws.write(0, 2, 'Wants to adjudicate?', f)
            if comp == BALLROOM or comp == LATIN:
                ws.write(0, 3, 'Has license?', f)
                ws.write(0, 4, 'Highest achieved level', f)
                ws.set_column(0, 4, 30)
                for d in range(0, len(adj)):
                    ws.write(d + 1, 0, adj[d].get_full_name())
                    ws.write(d + 1, 1, adj[d].contestant_info[0].team.name)
                    if comp == BALLROOM:
                        wants_to = adj[d].volunteer_info[0].jury_ballroom
                        lic = adj[d].volunteer_info[0].license_jury_ballroom
                        lvl = adj[d].volunteer_info[0].level_ballroom
                    else:
                        wants_to = adj[d].volunteer_info[0].jury_latin
                        lic = adj[d].volunteer_info[0].license_jury_latin
                        lvl = adj[d].volunteer_info[0].level_latin
                    ws.write(d + 1, 2, wants_to)
                    ws.write(d + 1, 3, lic)
                    ws.write(d + 1, 4, lvl)
            else:
                ws.set_column(0, 2, 30)
                for d in range(0, len(adj)):
                    ws.write(d + 1, 0, adj[d].get_full_name())
                    ws.write(d + 1, 1, adj[d].contestant_info[0].team.name)
                    if comp == SALSA:
                        wants_to = adj[d].volunteer_info[0].jury_salsa
                    else:
                        wants_to = adj[d].volunteer_info[0].jury_polka
                    ws.write(d + 1, 2, wants_to)
            ws.freeze_panes(1, 0)
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename=fn)
    return render_template('organizer/adjudicators_overview.html', ts=ts, data=data,
                           ballroom_adjudicators=ballroom_adjudicators, latin_adjudicators=latin_adjudicators,
                           salsa_adjudicators=salsa_adjudicators, polka_adjudicators=polka_adjudicators)
