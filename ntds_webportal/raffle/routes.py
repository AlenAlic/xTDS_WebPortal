from flask import render_template, request, flash, redirect, url_for, g, current_app
from flask_login import login_required, current_user
from ntds_webportal import db
from ntds_webportal.raffle import bp
from ntds_webportal.models import requires_access_level, requires_tournament_state, Team, Contestant, \
    User, Notification, requires_testing_environment
from ntds_webportal.raffle.forms import RaffleConfigurationForm
from ntds_webportal.data import *
from raffle_system.system import RaffleSystem
from raffle_system.functions import export_stats_list
import time


@bp.route('/configuration', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN], ACCESS[ORGANIZER]])
def configuration():
    form = RaffleConfigurationForm()
    if request.method == 'GET':
        form.populate()
    if request.method == 'POST':
        form.custom_validate()
    if form.validate_on_submit():
        form.save_settings()
        flash("Configuration saved.", "alert-success")
        if current_user.is_organizer():
            g.ts.raffle_system_configured = True
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('raffle/configuration.html', form=form)


@bp.route('/system', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def system():
    if not g.ts.main_raffle_taken_place:
        return redirect(url_for('raffle.start'))
    if g.ts.main_raffle_taken_place:
        if not g.ts.main_raffle_result_visible:
            return redirect(url_for('raffle.completed'))
        if g.ts.main_raffle_result_visible:
            return redirect(url_for('raffle.confirmed'))
    flash("Redirect to dashboard.")
    return redirect(url_for('main.dashboard'))


@bp.route('/start', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def start():
    if g.ts.main_raffle_taken_place:
        return redirect(url_for('raffle.completed'))
    raffle_sys = RaffleSystem()
    if request.method == 'GET':
        all_teams = db.session.query(Team).all()
        teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
                  'id_title': team.name.replace(' ', '-').replace('`', '') + '-title'} for team in all_teams]
        for t in teams:
            t['teamcaptains'] = [d for d in raffle_sys.registered_dancers
                                 if d.contestant_info[0].team == t['team'] and d.contestant_info[0].team_captain]
            t['available_dancers'] = [d for d in raffle_sys.registered_dancers
                                      if d.contestant_info[0].team == t['team']]
            t['guaranteed_dancers'] = [d for d in raffle_sys.guaranteed_dancers()
                                       if d.contestant_info[0].team == t['team']]
        return render_template('raffle/start.html', raffle_sys=raffle_sys, teams=teams)
    if request.method == 'POST':
        form = request.form
        if 'start_raffle' in form:
            raffle_sys.raffle()
            g.ts.main_raffle_taken_place = True
            flash('Raffle completed.', 'alert-info')
            db.session.commit()
        return redirect(url_for('raffle.system'))


@bp.route('/completed', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def completed():
    if not g.ts.main_raffle_taken_place:
        return redirect(url_for('raffle.start'))
    if g.ts.main_raffle_result_visible:
        return redirect(url_for('raffle.confirmed'))
    raffle_sys = RaffleSystem()
    if request.method == 'GET':
        all_teams = db.session.query(Team).all()
        teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
                  'id_title': team.name.replace(' ', '-').replace('`', '') + '-title'} for team in all_teams]
        for t in teams:
            t['available_dancers'] = [d for d in raffle_sys.registered_dancers
                                      if d.contestant_info[0].team == t['team']]
            t['selected_dancers'] = [d for d in raffle_sys.selected_dancers
                                     if d.contestant_info[0].team == t['team']]
            t['guaranteed_dancers'] = [d for d in raffle_sys.guaranteed_dancers()
                                       if d.contestant_info[0].team == t['team']]
        return render_template('raffle/completed.html', raffle_sys=raffle_sys, teams=teams)
    if request.method == 'POST':
        form = request.form
        if 'cancel_raffle' in form:
            for dancer in raffle_sys.all_dancers:
                dancer.status_info[0].set_status(REGISTERED)
            g.ts.main_raffle_taken_place = False
            flash('Raffle cancelled.', 'alert-info')
        elif 'confirm_raffle' in form:
            for dancer in raffle_sys.selected_dancers:
                dancer.status_info[0].set_status(SELECTED)
            g.ts.main_raffle_result_visible = True
            flash('Raffle confirmed. The results are now visible to the teamcaptains.', 'alert-success')
        elif 'balance_raffle' in form:
            raffle_sys.balance_raffle()
        elif 'finish_raffle' in form:
            raffle_sys.finish_raffle()
        elif 'finish_raffle_with_sleeping_spots' in form:
            raffle_sys.finish_raffle(non_sleeping_hall_dancers=True)
        elif 'select_random_group' in form:
            flash(raffle_sys.add_neutral_group())
        else:
            flash(raffle_sys.select_single_dancer(form))
        db.session.commit()
        return redirect(url_for('raffle.system'))


@bp.route('/confirmed', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def confirmed():
    if not g.ts.main_raffle_result_visible:
        return redirect(url_for('raffle.completed'))
    raffle_sys = RaffleSystem()
    if request.method == 'GET':
        all_teams = db.session.query(Team).all()
        teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
                  'id_title': team.name.replace(' ', '-').replace('`', '') + '-title'} for team in all_teams]
        for t in teams:
            t['available_dancers'] = [d for d in raffle_sys.registered_dancers
                                      if d.contestant_info[0].team == t['team']]
            t['selected_dancers'] = [d for d in raffle_sys.selected_dancers
                                     if d.contestant_info[0].team == t['team']]
            t['confirmed_dancers'] = [d for d in raffle_sys.confirmed_dancers
                                      if d.contestant_info[0].team == t['team']]
        return render_template('raffle/confirmed.html', raffle_sys=raffle_sys, teams=teams)
    if request.method == 'POST':
        form = request.form
        if 'select_marked_dancers' in form:
            raffle_sys.confirm_selection([d for d in raffle_sys.selected_dancers if str(d.contestant_id) in form])
        elif 'remove_marked_dancers' in form:
            raffle_sys.cancel_selection([d for d in raffle_sys.all_dancers if str(d.contestant_id) in form])
        elif 'balance_raffle' in form:
            raffle_sys.balance_raffle()
        elif 'finish_raffle' in form:
            raffle_sys.finish_raffle()
        elif 'finish_raffle_with_sleeping_spots' in form:
            raffle_sys.finish_raffle(non_sleeping_hall_dancers=True)
        elif 'select_random_group' in form:
            flash(raffle_sys.add_neutral_group())
        else:
            flash(raffle_sys.select_single_dancer(form))
        db.session.commit()
        return redirect(url_for('raffle.system'))


@bp.route('/cancel_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def cancel_dancer(number):
    changed_dancer = db.session.query(Contestant).filter(Contestant.contestant_id == number).first()
    changed_dancer.cancel_registration()
    team_captain = User.query.filter(User.access == ACCESS[TEAM_CAPTAIN],
                                     User.team == changed_dancer.contestant_info[0].team).first()
    db.session.commit()
    flash('The registration of {} has been cancelled.'.format(changed_dancer.get_full_name()), 'alert-info')
    text = f"{changed_dancer.get_full_name()}' registration has been cancelled by the organization.\n"
    n = Notification(title=f"Cancelled registration of {changed_dancer.get_full_name()}", text=text,
                     user=team_captain)
    n.send()
    return redirect(url_for('raffle.system'))


@bp.route('/confirm_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def confirm_dancer(number):
    changed_dancer = db.session.query(Contestant).filter(Contestant.contestant_id == number).first()
    changed_dancer.status_info[0].set_status(CONFIRMED)
    team_captain = User.query.filter(User.access == ACCESS[TEAM_CAPTAIN],
                                     User.team == changed_dancer.contestant_info[0].team).first()
    db.session.commit()
    flash(f"{changed_dancer.get_full_name()} has been confirmed.", 'alert-info')
    text = f"{changed_dancer.get_full_name()}' has been confirmed by the organization.\n"
    n = Notification(title=f"Confirmation of {changed_dancer.get_full_name()}", text=text, user=team_captain)
    n.send()
    return redirect(url_for('raffle.system'))


@bp.route('/test_system', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def test_system():
    if not g.ts.main_raffle_taken_place:
        return redirect(url_for('raffle.test_start'))
    if g.ts.main_raffle_taken_place:
        if not g.ts.main_raffle_result_visible:
            return redirect(url_for('raffle.test_completed'))
        if g.ts.main_raffle_result_visible:
            return redirect(url_for('raffle.test_confirmed'))
    flash("Redirect to dashboard.")
    return redirect(url_for('main.dashboard'))


@bp.route('/test_start', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def test_start():
    if g.ts.main_raffle_taken_place:
        return redirect(url_for('raffle.test_completed'))
    commit_accessible = current_app.config.get('ENV') in TESTING_ENVIRONMENTS
    raffle_sys = RaffleSystem()
    if request.method == 'GET':
        return render_template('raffle/test_start.html', raffle_sys=raffle_sys, commit_accessible=commit_accessible)
    if request.method == 'POST':
        form = request.form
        if commit_accessible:
            if 'start_raffle' in form:
                raffle_sys.raffle()
                g.ts.main_raffle_taken_place = True
                flash('Raffle completed.', 'alert-info')
                db.session.commit()
        if 'start_test_raffle' in form:
            raffle_sys.test = True
            raffle_sys.raffle()
        if 'start_batch_raffle' in form:
            runs = 100
            raffle_sys.batch = True
            start_time = time.time()
            for i in range(0, runs):
                print(f'Performing run {i+1} of {runs}...')
                raffle_sys.raffle()
                raffle_sys = RaffleSystem()
                raffle_sys.batch = True
            print(f"--- {runs} raffles done in %.3f seconds ---" % (time.time() - start_time))
            export_stats_list()
        return redirect(url_for('raffle.test_start'))


@bp.route('/test_completed', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
@requires_testing_environment
def test_completed():
    if not g.ts.main_raffle_taken_place:
        return redirect(url_for('raffle.test_start'))
    if g.ts.main_raffle_result_visible:
        return redirect(url_for('raffle.test_confirmed'))
    raffle_sys = RaffleSystem()
    if request.method == 'GET':
        all_teams = db.session.query(Team).all()
        teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
                  'id_title': team.name.replace(' ', '-').replace('`', '') + '-title'} for team in all_teams]
        for t in teams:
            t['available_dancers'] = [d for d in raffle_sys.registered_dancers
                                      if d.contestant_info[0].team == t['team']]
            t['selected_dancers'] = [d for d in raffle_sys.selected_dancers
                                     if d.contestant_info[0].team == t['team']]
            t['guaranteed_dancers'] = [d for d in raffle_sys.guaranteed_dancers()
                                       if d.contestant_info[0].team == t['team']]
        return render_template('raffle/test_completed.html', raffle_sys=raffle_sys, teams=teams)
    if request.method == 'POST':
        form = request.form
        if 'cancel_raffle' in form:
            for dancer in raffle_sys.all_dancers:
                dancer.status_info[0].set_status(REGISTERED)
            g.ts.main_raffle_taken_place = False
            flash('Raffle cancelled.', 'alert-info')
        elif 'confirm_raffle' in form:
            for dancer in raffle_sys.selected_dancers:
                dancer.status_info[0].set_status(SELECTED)
            g.ts.main_raffle_result_visible = True
            flash('Raffle confirmed. The results are now visible to the teamcaptains.', 'alert-success')
        elif 'balance_raffle' in form:
            raffle_sys.balance_raffle()
        elif 'finish_raffle' in form:
            raffle_sys.finish_raffle()
        elif 'finish_raffle_with_sleeping_spots' in form:
            raffle_sys.finish_raffle(non_sleeping_hall_dancers=True)
        elif 'select_random_group' in form:
            flash(raffle_sys.add_neutral_group())
        else:
            flash(raffle_sys.select_single_dancer(form))
        db.session.commit()
        return redirect(url_for('raffle.test_system'))


@bp.route('/test_confirmed', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
@requires_testing_environment
def test_confirmed():
    if not g.ts.main_raffle_result_visible:
        return redirect(url_for('raffle.test_completed'))
    raffle_sys = RaffleSystem()
    if request.method == 'GET':
        all_teams = db.session.query(Team).all()
        teams = [{'team': team, 'id': team.name.replace(' ', '-').replace('`', ''),
                  'id_title': team.name.replace(' ', '-').replace('`', '') + '-title'} for team in all_teams]
        for t in teams:
            t['available_dancers'] = [d for d in raffle_sys.registered_dancers
                                      if d.contestant_info[0].team == t['team']]
            t['selected_dancers'] = [d for d in raffle_sys.selected_dancers
                                     if d.contestant_info[0].team == t['team']]
            t['confirmed_dancers'] = [d for d in raffle_sys.confirmed_dancers
                                      if d.contestant_info[0].team == t['team']]
        return render_template('raffle/test_confirmed.html', raffle_sys=raffle_sys, teams=teams)
    if request.method == 'POST':
        form = request.form
        if 'reset_raffle' in form:
            for dancer in raffle_sys.all_dancers:
                dancer.status_info[0].set_status(REGISTERED)
            g.ts.main_raffle_taken_place = False
            g.ts.main_raffle_result_visible = False
            g.ts.raffle_completed_message_sent = False
            flash('Raffle results cleared.', 'alert-info')
        elif 'select_marked_dancers' in form:
            raffle_sys.confirm_selection([d for d in raffle_sys.selected_dancers if str(d.contestant_id) in form])
        elif 'remove_marked_dancers' in form:
            raffle_sys.cancel_selection([d for d in raffle_sys.all_dancers if str(d.contestant_id) in form])
        elif 'balance_raffle' in form:
            raffle_sys.balance_raffle()
        elif 'finish_raffle' in form:
            raffle_sys.finish_raffle()
        elif 'finish_raffle_with_sleeping_spots' in form:
            raffle_sys.finish_raffle(non_sleeping_hall_dancers=True)
        elif 'select_random_group' in form:
            flash(raffle_sys.add_neutral_group())
        else:
            flash(raffle_sys.select_single_dancer(form))
        db.session.commit()
        return redirect(url_for('raffle.test_system'))
