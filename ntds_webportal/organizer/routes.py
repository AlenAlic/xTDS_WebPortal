from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.organizer import bp
from ntds_webportal.models import requires_access_level, Team, TeamFinances, Contestant, ContestantInfo, DancingInfo,\
    StatusInfo, NameChangeRequest
import ntds_webportal.data as data
from ntds_webportal.functions import uniquify, check_combination, get_combinations_list
from ntds_webportal.data import *
from raffle_system.system import raffle, finish_raffle, raffle_add_neutral_group, test_raffle
from raffle_system.functions import RaffleSystem, get_combinations
from ntds_webportal.organizer.forms import NameChangeResponse
import time
import random
from sqlalchemy import and_, or_


@bp.route('/registration_overview')
@login_required
@requires_access_level([data.ACCESS['organizer']])
def registration_overview():
    # TODO speed up render
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .order_by(ContestantInfo.team_id, ContestantInfo.number).all()
    all_teams = db.session.query(Team).all()
    order = [CONFIRMED, SELECTED, REGISTERED, CANCELLED]
    all_dancers = sorted(all_dancers, key=lambda o: (o.contestant_info[0].team_id,
                                                     order.index(o.status_info[0].status)))
    dancers = [{'country': team.country, 'name': team.name, 'id': team.name.replace(' ', '-').replace('`', ''),
                'dancers': db.session.query(Contestant).join(ContestantInfo).filter(ContestantInfo.team == team).all()}
               for team in all_teams]
    dancers = [d for d in dancers if len(d['dancers']) > 0]
    dutch_dancers = [team for team in dancers if team['country'] == data.NETHERLANDS]
    german_dancers = [team for team in dancers if team['country'] == data.GERMANY]
    other_dancers = [team for team in dancers if team['country'] != data.NETHERLANDS and
                     team['country'] != data.GERMANY]
    return render_template('organizer/registration_overview.html', data=data, all_dancers=all_dancers,
                           dutch_dancers=dutch_dancers, german_dancers=german_dancers, other_dancers=other_dancers)


@bp.route('/finances_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['organizer']])
def finances_overview():
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .filter(StatusInfo.payment_required.is_(True)).order_by(ContestantInfo.team_id, ContestantInfo.number).all()
    all_confirmed_dancers = [d for d in all_dancers if d.status_info[0].status == CONFIRMED]
    all_cancelled_dancers = [d for d in all_dancers if d.status_info[0].status == CANCELLED]
    all_teams = db.session.query(Team).join(TeamFinances).all()
    teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
              'confirmed_dancers': [dancer for dancer in all_confirmed_dancers if
                                    dancer.contestant_info[0].team.name == team.name],
              'cancelled_dancers': [dancer for dancer in all_cancelled_dancers if
                                    dancer.contestant_info[0].team.name == team.name],
              'finances': data.finances_overview([dancer for dancer in all_dancers if
                                                  dancer.contestant_info[0].team.name == team.name])}
             for team in all_teams]
    teams = [team for team in teams if (len(team['confirmed_dancers'])+len(team['cancelled_dancers'])) > 0]
    dutch_teams = [team for team in teams if team['team'].country == data.NETHERLANDS]
    german_teams = [team for team in teams if team['team'].country == data.GERMANY]
    other_teams = [team for team in teams if
                   team['team'].country != data.NETHERLANDS and team['team'].country != data.GERMANY]
    if request.method == 'POST':
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


@bp.route('/name_change_list', methods=['GET'])
@login_required
@requires_access_level([data.ACCESS['organizer']])
def name_change_list():
    nml = NameChangeRequest.query.filter_by(state=NameChangeRequest.STATE['Open']).all()
    return render_template('organizer/name_change_list.html', list=nml)


@bp.route('/name_change_respond/<req>', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['organizer']])
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
@requires_access_level([data.ACCESS['organizer']])
def raffle_system():
    raffle_sys = RaffleSystem()
    state = raffle_sys.state
    raffle_config = raffle_sys.raffle_config
    tournament_config = raffle_sys.tournament_config

    newly_selected = None
    stats_registered, stats_selected, stats_confirmed = None, None, None
    stats_registered = raffle_sys.get_stats(REGISTERED)
    if state.main_raffle_taken_place:
        stats_selected = raffle_sys.get_stats(SELECTED)
        stats_confirmed = raffle_sys.get_stats(CONFIRMED)

    selected_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.raffle_status == SELECTED)\
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    confirmed_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.raffle_status == CONFIRMED)\
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    available_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.raffle_status == REGISTERED)\
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()

    combination_dancers = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(StatusInfo.raffle_status == REGISTERED, DancingInfo.partner.is_(None)) \
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    available_combinations_list = [get_combinations(d) for d in combination_dancers]
    available_combinations = {comb: 0 for comb in uniquify(available_combinations_list)}
    for comb in available_combinations_list:
        available_combinations[comb] += 1

    all_teams = db.session.query(Team).all()
    teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
              'id_title': team.name.replace(' ', '-').replace('`', '') + '-title'} for team in all_teams]
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
            .order_by(Contestant.contestant_id).all()

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
            flash('Raffle results cleared.', 'alert-info')
        elif 'finish_raffle' in form:
            finish_raffle(raffle_sys)
        elif 'select_random_group' in form:
            flash(raffle_add_neutral_group(raffle_sys))
        elif 'select_marked_dancers' in form:
            marked_dancers = [d for d in all_dancers if str(d.contestant_id) in form]
            for dancer in marked_dancers:
                dancer.status_info[0].set_status(SELECTED)
        elif 'remove_marked_dancers' in form:
            marked_dancers = [d for d in all_dancers if str(d.contestant_id) in form]
            for dancer in marked_dancers:
                dancer.status_info[0].set_status(REGISTERED)
        elif 'start_test_raffle' in form:
            runs = 25
            if True:
                start_time = time.time()
                for i in range(0, runs):
                    print(f'Performing run {i+1} of {runs}...')
                    test_raffle()
                print(f"--- {runs} raffles done in %.3f seconds ---" % (time.time() - start_time))
            else:
                test_raffle()
        else:
            if not raffle_sys.full():
                try:
                    s = [f for f in form][0]
                except IndexError:
                    pass
                else:
                    s = get_combinations_list(s)
                    single_dancers = [d for d in available_dancers if check_combination(d, s)]
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
                           available_combinations=available_combinations, newly_selected=newly_selected)
