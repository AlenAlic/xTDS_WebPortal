from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.organizer import bp
from ntds_webportal.models import requires_access_level, Team, TeamFinances, Contestant, ContestantInfo, StatusInfo, \
    NameChangeRequest, TournamentState
import ntds_webportal.data as data
from raffle_system.system import raffle, test_raffle
from raffle_system.functions import DancerLists
from ntds_webportal.organizer.forms import NameChangeResponse
import time


@bp.route('/registration_overview')
@login_required
@requires_access_level([data.ACCESS['organizer']])
def registration_overview():
    # TODO speed up render
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .order_by(ContestantInfo.team_id, ContestantInfo.number).all()
    all_teams = db.session.query(Team).all()
    # order = [data.CONFIRMED, data.SELECTED, data.REGISTERED, data.CANCELLED]
    # all_dancers = sorted(all_dancers, key=lambda o: (o.contestant_info[0].team_id,
    #                                                  order.index(o.status_info[0].status)))
    start_time = time.time()
    print("Order done in %.3f seconds ---" % (time.time() - start_time))
    dancers = [{'country': team.country, 'name': team.name, 'id': team.name.replace(' ', '-').replace('`', ''),
                'dancers': db.session.query(Contestant).join(ContestantInfo).filter(ContestantInfo.team == team).all()}
               for team in all_teams]
    # dancers = [d for d in dancers if len(d['dancers']) > 0]
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
    all_confirmed_dancers = [d for d in all_dancers if d.status_info[0].status == data.CONFIRMED]
    all_cancelled_dancers = [d for d in all_dancers if d.status_info[0].status == data.CANCELLED]
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
    state = TournamentState.query.first()
    tournament_config = state.get_tournament_config()
    raffle_config = state.get_raffle_config()
    all_teams = db.session.query(Team).all()
    teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
              'id_title': team.name.replace(' ', '-').replace('`', '') + '-title',
              'dancers': db.session.query(Contestant).join(ContestantInfo).filter(ContestantInfo.team == team).all(),
              'selected_dancers': db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)
             .filter(ContestantInfo.team == team, StatusInfo.raffle_status == data.SELECTED).all(),
              'confirmed_dancers': db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)
             .filter(ContestantInfo.team == team, StatusInfo.raffle_status == data.CONFIRMED).all()}
             for team in all_teams]
    teams = [team for team in teams if (len(team['dancers'])) > 0]
    if state.main_raffle_taken_place:
        dl = DancerLists()
        stats_selected, stats_confirmed = dl.get_stats()
    else:
        stats_selected, stats_confirmed = None, None
    if request.method == 'POST':
        all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(StatusInfo.status != data.CANCELLED).order_by(ContestantInfo.team_id, Contestant.first_name).all()
        form = request.form
        if 'raffle_config' in form:
            for k, v in form.items():
                if k in raffle_config:
                    raffle_config[k] = v
            state.set_raffle_config(raffle_config)
        elif 'start_raffle' in form:
            guaranteed_dancers = [d for d in all_dancers if str(d.contestant_id) in form]
            raffle(guaranteed_dancers)
            state.main_raffle_taken_place = True
            flash('Raffle completed.', 'alert-info')
        elif 'cancel_raffle' in form:
            for dancer in all_dancers:
                dancer.status_info[0].set_status(data.REGISTERED)
            state.main_raffle_taken_place = False
            flash('Raffle cancelled.', 'alert-info')
        elif 'redo_raffle' in form:
            # TODO add guaranteed dancers to model
            for dancer in all_dancers:
                dancer.status_info[0].set_status(data.REGISTERED)
            raffle()
            flash('Raffle completed.', 'alert-info')
        elif 'confirm_raffle' in form:
            selected_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
                .filter(StatusInfo.raffle_status == data.SELECTED) \
                .order_by(ContestantInfo.team_id, Contestant.first_name).all()
            for dancer in selected_dancers:
                dancer.status_info[0].set_status(data.SELECTED)
            state.main_raffle_result_visible = True
            flash('Raffle confirmed. The results are now visible to the teamcaptains.', 'alert-success')
        elif 'reset_raffle' in form:
            for dancer in all_dancers:
                dancer.status_info[0].set_status(data.REGISTERED)
            state.main_raffle_taken_place = False
            state.main_raffle_result_visible = False
            flash('Raffle results cleared.', 'alert-info')
        else:
            max_id = db.session.query().with_entities(db.func.max(Contestant.contestant_id)).scalar()
            dancer_ids = list(range(0, max_id+1))
            selected = {did: 0 for did in dancer_ids}
            runs = 100
            if False:
                start_time = time.time()
                for i in range(0, runs):
                    print(f'Performing run {i+1} of {runs}...')
                    selected = test_raffle(selected)
                    with open('stats.txt', 'a', encoding='utf-8') as f1:
                        f1.write(str(selected) + '\n')
                print("--- Done in %.3f seconds ---" % (time.time() - start_time))
            else:
                test_raffle(selected)
        db.session.commit()
        return redirect(url_for('organizer.raffle_system'))
    return render_template('organizer/raffle_system.html', state=state, data=data,
                           tournament_config=tournament_config, raffle_config=raffle_config, teams=teams,
                           stats_selected=stats_selected, stats_confirmed=stats_confirmed)
