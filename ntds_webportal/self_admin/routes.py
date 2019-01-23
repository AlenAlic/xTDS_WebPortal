from flask import render_template, request, redirect, url_for, flash, g, current_app
from flask_login import login_required, current_user, logout_user, login_user
from ntds_webportal import db
from ntds_webportal.self_admin import bp
from ntds_webportal.self_admin.forms import SwitchUserForm, CreateOrganizerForm, EditOrganizerForm, CreateTeamForm, \
    CreateTeamCaptainAccountForm, SystemSetupForm, ResetOrganizerAccountForm
from ntds_webportal.models import requires_access_level, User, Team, SystemConfiguration, Contestant, \
    StatusInfo, AttendedPreviousTournamentContestant, NotSelectedContestant, EXCLUDED_FROM_CLEARING, \
    requires_testing_environment, Event
from ntds_webportal.functions import str2bool, reset_tournament_state, \
    make_system_configuration_accessible_to_organizer, generate_maintenance_page
from ntds_webportal.auth.email import send_organizer_activation_email
from ntds_webportal.functions import random_password
from ntds_webportal.data import *
import ntds_webportal.data as data
from instance.test_populate import populate_test_data
from sqlalchemy import or_, case, exists
import datetime


@bp.route('/system_setup', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def system_setup():
    organizer = User.query.filter(User.access == ACCESS[ORGANIZER]).first()
    sc = SystemConfiguration.query.first()
    reset_organizer_account_form = ResetOrganizerAccountForm()
    if request.method == 'POST':
        reset_organizer_account_form.username.data = reset_organizer_account_form.tournament.data + \
                                                     reset_organizer_account_form.city.data + \
                                                     str(reset_organizer_account_form.year.data)
    elif request.method == 'GET':
        reset_organizer_account_form.tournament.data = sc.tournament
        reset_organizer_account_form.year.data = sc.year
        reset_organizer_account_form.city.data = sc.city
        reset_organizer_account_form.username.data = sc.tournament + sc.city + str(sc.year)
        tsd = datetime.datetime.utcfromtimestamp(sc.tournament_starting_date)
        reset_organizer_account_form.tournament_starting_date.data = datetime.date(tsd.year, tsd.month, tsd.day)
    if reset_organizer_account_form.validate_on_submit():
        sc.tournament = reset_organizer_account_form.tournament.data
        sc.year = reset_organizer_account_form.year.data
        sc.city = reset_organizer_account_form.city.data
        tsd = datetime.datetime(reset_organizer_account_form.tournament_starting_date.data.year,
                                reset_organizer_account_form.tournament_starting_date.data.month,
                                reset_organizer_account_form.tournament_starting_date.data.day, 0, 0, 0, 0)
        sc.tournament_starting_date = tsd.replace(tzinfo=datetime.timezone.utc).timestamp()

        organizer.username = reset_organizer_account_form.username.data
        organizer.email = reset_organizer_account_form.email.data
        organizer_pass = random_password()
        organizer.set_password(organizer_pass)
        organizer.send_new_messages_email = True
        organizer.is_active = True
        assistants = User.query.filter(or_(User.access == ACCESS[BLIND_DATE_ASSISTANT],
                                           User.access == ACCESS[CHECK_IN_ASSISTANT],
                                           User.access == ACCESS[ADJUDICATOR_ASSISTANT],
                                           User.access == ACCESS[TOURNAMENT_OFFICE_MANAGER],
                                           User.access == ACCESS[FLOOR_MANAGER])).all()
        for assistant in assistants:
            assistant.is_active = True
        db.session.commit()
        g.ts.organizer_account_set = True
        db.session.commit()
        event = Event()
        event.name = f"{sc.tournament} {sc.year} {sc.city}"
        db.session.add(event)
        db.session.commit()
        send_organizer_activation_email(organizer.email, organizer.username, organizer_pass,
                                        tournament=reset_organizer_account_form.tournament.data,
                                        year=reset_organizer_account_form.year.data,
                                        city=reset_organizer_account_form.city.data)
        flash(f"Organizer account has been reset. Login credentials have been sent to {organizer.email}.",
              "alert-success")
        make_system_configuration_accessible_to_organizer()
        return redirect(url_for('main.dashboard'))
    else:
        form = request.args
        if 'reset_website' in form:
            dancer_accounts = User.query.filter(User.access == ACCESS[DANCER]).all()
            for dancer in dancer_accounts:
                db.session.delete(dancer)
            db.session.commit()
            super_volunteer_accounts = User.query.filter(User.access == ACCESS[SUPER_VOLUNTEER]).all()
            for super_volunteer in super_volunteer_accounts:
                db.session.delete(super_volunteer)
            db.session.commit()
            non_admins = User.query.filter(User.access > ACCESS[ADMIN]).all()
            for na in non_admins:
                na.is_active = False
            treasurers = User.query.filter(User.access == ACCESS[TREASURER]).all()
            for treasurer in treasurers:
                treasurer.password_hash = None
                treasurer.email = None
            assistants = User.query.filter(or_(User.access == ACCESS[BLIND_DATE_ASSISTANT],
                                               User.access == ACCESS[CHECK_IN_ASSISTANT],
                                               User.access == ACCESS[ADJUDICATOR_ASSISTANT],
                                               User.access == ACCESS[TOURNAMENT_OFFICE_MANAGER],
                                               User.access == ACCESS[FLOOR_MANAGER])).all()
            for assistant in assistants:
                assistant.set_password(random_password())
            db.session.commit()
            teams = Team.query.all()
            for team in teams:
                team.amount_paid = 0
            db.session.commit()
            dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == CONFIRMED,
                                                               StatusInfo.checked_in.is_(True)).all()
            for dancer in dancers:
                dancer.email = dancer.email.lower()
            for dancer in dancers:
                check_attendee = AttendedPreviousTournamentContestant.query\
                    .filter(AttendedPreviousTournamentContestant.email == dancer.email).first()
                if check_attendee is None:
                    attendee = AttendedPreviousTournamentContestant()
                    attendee.first_name = dancer.first_name
                    attendee.prefixes = dancer.prefixes
                    attendee.last_name = dancer.last_name
                    attendee.email = dancer.email.lower()
                    attendee.set_tournaments(organizer.username)
                    db.session.add(attendee)
                else:
                    check_attendee.set_tournaments(organizer.username)
            db.session.commit()
            nsd = NotSelectedContestant.query.filter(NotSelectedContestant.tournament == g.sc.tournament).all()
            for dancer in nsd:
                db.session.delete(dancer)
            db.session.commit()
            dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == REGISTERED).all()
            for dancer in dancers:
                dancer.email = dancer.email.lower()
            for dancer in dancers:
                check_attendee = NotSelectedContestant.query.filter(NotSelectedContestant.email == dancer.email).first()
                if check_attendee is None:
                    attendee = NotSelectedContestant()
                    attendee.first_name = dancer.first_name
                    attendee.prefixes = dancer.prefixes
                    attendee.last_name = dancer.last_name
                    attendee.email = dancer.email.lower()
                    attendee.tournament = g.sc.tournament
                    db.session.add(attendee)
            db.session.commit()
            reset_tournament_state()
            db.session.commit()
            with current_app.app_context():
                meta = db.metadata
                for table in reversed(meta.sorted_tables):
                    if table.name not in EXCLUDED_FROM_CLEARING:
                        print('Cleared table {}.'.format(table))
                        db.session.execute(table.delete())
                        if not current_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:'):
                            db.session.execute(f"ALTER TABLE {table.name} AUTO_INCREMENT = 1;")
                db.session.commit()
            flash("xTDS WebPortal has been reset.", "alert-success")
        if 'access_system_configuration' in form:
            make_system_configuration_accessible_to_organizer()
        if len(form) > 0:
            return redirect(url_for('main.dashboard'))
    return render_template('admin/system_setup.html', roa_form=reset_organizer_account_form)


@bp.route('/system_configuration', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN], ACCESS[ORGANIZER]])
def system_configuration():
    if current_user.is_organizer() and g.ts.registration_period_started:
        flash('Page currently inaccessible. The registration has started. For emergency access, contact the admin.')
        return redirect(url_for('main.dashboard'))
    form = SystemSetupForm()
    if request.method == 'GET':
        form.tournament.data = g.sc.tournament
        form.year.data = g.sc.year
        form.city.data = g.sc.city
        tsd = datetime.datetime.utcfromtimestamp(g.sc.tournament_starting_date)
        form.tournament_starting_date.data = datetime.date(tsd.year, tsd.month, tsd.day)

        form.main_page_link.data = g.sc.main_page_link
        form.terms_and_conditions_link.data = g.sc.terms_and_conditions_link

        form.number_of_teamcaptains.data = g.sc.number_of_teamcaptains

        form.beginners_level.data = str(g.sc.beginners_level)
        form.closed_level.data = str(g.sc.closed_level)
        form.breitensport_obliged_blind_date.data = str(g.sc.breitensport_obliged_blind_date)
        form.salsa_competition.data = str(g.sc.salsa_competition)
        form.polka_competition.data = str(g.sc.polka_competition)

        form.student_price.data = g.sc.student_price
        form.non_student_price.data = g.sc.non_student_price
        form.phd_student_category.data = str(g.sc.phd_student_category)
        form.phd_student_price.data = g.sc.phd_student_price

        form.finances_full_refund.data = str(g.sc.finances_full_refund)
        form.finances_partial_refund.data = str(g.sc.finances_partial_refund)
        form.finances_partial_refund_percentage.data = g.sc.finances_partial_refund_percentage
        frd = datetime.datetime.utcfromtimestamp(g.sc.finances_refund_date)
        form.finances_refund_date.data = datetime.date(frd.year, frd.month, frd.day)

        form.first_time_ask.data = str(g.sc.first_time_ask)
        form.ask_diet_allergies.data = str(g.sc.ask_diet_allergies)
        form.ask_volunteer.data = str(g.sc.ask_volunteer)
        form.ask_first_aid.data = str(g.sc.ask_first_aid)
        form.ask_emergency_response_officer.data = str(g.sc.ask_emergency_response_officer)
        form.ask_adjudicator_highest_achieved_level.data = str(g.sc.ask_adjudicator_highest_achieved_level)
        form.ask_adjudicator_certification.data = str(g.sc.ask_adjudicator_certification)

        form.t_shirt_sold.data = str(g.sc.t_shirt_sold)
        form.t_shirt_price.data = g.sc.t_shirt_price
        form.mug_sold.data = str(g.sc.mug_sold)
        form.mug_price.data = g.sc.mug_price
        form.bag_sold.data = str(g.sc.bag_sold)
        form.bag_price.data = g.sc.bag_price
        form.merchandise_link.data = g.sc.merchandise_link
        mcd = datetime.datetime.utcfromtimestamp(g.sc.merchandise_closing_date)
        mcd += datetime.timedelta(days=-1)
        form.merchandise_closing_date.data = datetime.date(mcd.year, mcd.month, mcd.day)
    elif request.method == 'POST':
        if current_user.is_organizer():
            form.tournament.data = g.sc.tournament
            form.year.data = g.sc.year
            form.city.data = g.sc.city
            tsd = datetime.datetime.utcfromtimestamp(g.sc.tournament_starting_date)
            form.tournament_starting_date.data = datetime.date(tsd.year, tsd.month, tsd.day)
        if str2bool(form.finances_full_refund.data):
            form.finances_partial_refund.data = str(False)
            form.finances_partial_refund_percentage.data = 100
        if not str2bool(form.finances_full_refund.data) and not str2bool(form.finances_partial_refund.data):
            # form.finances_refund_date.data = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
            form.finances_refund_date.data = datetime.date.today()
    if form.validate_on_submit():
        g.sc.tournament = form.tournament.data
        g.sc.year = form.year.data
        g.sc.city = form.city.data
        tsd = datetime.datetime(form.tournament_starting_date.data.year, form.tournament_starting_date.data.month,
                                form.tournament_starting_date.data.day, 3, 0, 0, 0)
        g.sc.tournament_starting_date = tsd.replace(tzinfo=datetime.timezone.utc).timestamp()

        g.sc.main_page_link = form.main_page_link.data
        g.sc.terms_and_conditions_link = form.terms_and_conditions_link.data

        g.sc.number_of_teamcaptains = form.number_of_teamcaptains.data

        g.sc.beginners_level = str2bool(form.beginners_level.data)
        g.sc.closed_level = str2bool(form.closed_level.data)
        g.sc.breitensport_obliged_blind_date = str2bool(form.breitensport_obliged_blind_date.data)
        g.sc.salsa_competition = str2bool(form.salsa_competition.data)
        g.sc.polka_competition = str2bool(form.polka_competition.data)

        g.sc.student_price = form.student_price.data
        g.sc.non_student_price = form.non_student_price.data
        g.sc.phd_student_category = str2bool(form.phd_student_category.data)
        g.sc.phd_student_price = form.phd_student_price.data

        g.sc.finances_full_refund = str2bool(form.finances_full_refund.data)
        g.sc.finances_partial_refund = str2bool(form.finances_partial_refund.data)
        g.sc.finances_partial_refund_percentage = form.finances_partial_refund_percentage.data
        frd = datetime.datetime(form.finances_refund_date.data.year, form.finances_refund_date.data.month,
                                form.finances_refund_date.data.day, 3, 0, 0, 0)
        g.sc.finances_refund_date = frd.replace(tzinfo=datetime.timezone.utc).timestamp()

        g.sc.first_time_ask = str2bool(form.first_time_ask.data)
        g.sc.ask_diet_allergies = str2bool(form.ask_diet_allergies.data)
        g.sc.ask_volunteer = str2bool(form.ask_volunteer.data)
        g.sc.ask_first_aid = str2bool(form.ask_first_aid.data)
        g.sc.ask_emergency_response_officer = str2bool(form.ask_emergency_response_officer.data)
        g.sc.ask_adjudicator_highest_achieved_level = str2bool(form.ask_adjudicator_highest_achieved_level.data)
        g.sc.ask_adjudicator_certification = str2bool(form.ask_adjudicator_certification.data)

        g.sc.t_shirt_sold = str2bool(form.t_shirt_sold.data)
        g.sc.t_shirt_price = form.t_shirt_price.data
        g.sc.mug_sold = str2bool(form.mug_sold.data)
        g.sc.mug_price = form.mug_price.data
        g.sc.bag_sold = str2bool(form.bag_sold.data)
        g.sc.bag_price = form.bag_price.data
        g.sc.merchandise_link = form.merchandise_link.data
        if not str2bool(form.t_shirt_sold.data) and not str2bool(form.mug_sold.data) and \
                not str2bool(form.bag_sold.data):
            g.sc.merchandise_closing_date = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
        else:
            mcd = datetime.datetime(form.merchandise_closing_date.data.year, form.merchandise_closing_date.data.month,
                                    form.merchandise_closing_date.data.day, 3, 0, 0, 0)
            mcd += datetime.timedelta(days=1)
            g.sc.merchandise_closing_date = mcd.replace(tzinfo=datetime.timezone.utc).timestamp()

        db.session.commit()
        flash("Configuration saved.", "alert-success")
        if g.ts.system_configured:
            g.sc.system_configuration_accessible = False
        else:
            g.ts.system_configured = True
        db.session.commit()
        if current_user.is_organizer():
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('self_admin.system_configuration'))
    return render_template('admin/system_configuration.html', form=form)


@bp.route('/switch_user', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def switch_user():
    form = SwitchUserForm()
    form.user.label.text = 'Switch to a non-Dutch team captain'
    form.submit.label.text = 'Switch to team captain'
    users = User.query.join(Team).filter(User.is_active.is_(True), User.user_id != current_user.user_id,
                                         or_(User.access == ACCESS[TEAM_CAPTAIN], User.access == ACCESS[TREASURER]),
                                         Team.country != NETHERLANDS).order_by(Team.city).all()
    form.user.choices = map(lambda user_map: (user_map.user_id, user_map.username), users)
    dancer_super_volunteer_form = SwitchUserForm()
    dancer_super_volunteer_form.user.label.text = 'Switch to a dancer or Super Volunteer User account'
    dancer_super_volunteer_users = User.query\
        .filter(User.is_active.is_(True), or_(User.access == ACCESS[DANCER], User.access == ACCESS[SUPER_VOLUNTEER]))\
        .all()
    dancer_super_volunteer_choices = [(u.user_id, u.dancer.get_full_name()) for u in dancer_super_volunteer_users
                                      if u.dancer is not None]
    dancer_super_volunteer_choices += [(u.user_id, u.super_volunteer.get_full_name()) for u
                                       in dancer_super_volunteer_users if u.super_volunteer is not None]
    dancer_super_volunteer_choices.sort(key=lambda x: x[1])
    dancer_super_volunteer_choices = [(0, 'Choose an account to switch to.')] + dancer_super_volunteer_choices
    dancer_super_volunteer_form.user.choices = dancer_super_volunteer_choices
    if form.validate_on_submit():
        user = User.query.filter(User.user_id == form.user.data).first()
        if user is not None:
            logout_user()
            login_user(user)
        else:
            flash('User account is not active.')
        return redirect(url_for('main.index'))
    if dancer_super_volunteer_form.validate_on_submit():
        user = User.query.filter(User.user_id == form.user.data).first()
        if user is not None:
            logout_user()
            login_user(user)
        else:
            flash('User account is not active.')
        return redirect(url_for('main.index'))
    return render_template('admin/switch_user.html', form=form, dancer_super_volunteer_form=dancer_super_volunteer_form)


@bp.route('/switch_to_organizer', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def switch_to_organizer():
    user = User.query.filter(User.is_active.is_(True), User.access == ACCESS[ORGANIZER]).first()
    if user is not None:
        logout_user()
        login_user(user)
    else:
        flash('User account is not active.')
    return redirect(url_for('main.index'))


@bp.route('/switch_to_team_captain/<name>', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def switch_to_team_captain(name):
    user = User.query.join(Team).filter(User.is_active.is_(True), User.access == ACCESS[TEAM_CAPTAIN],
                                        Team.name == name).first()
    if user is not None:
        logout_user()
        login_user(user)
    else:
        flash('User account is not active.')
    return redirect(url_for('main.index'))


@bp.route('/user_list', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def user_list():
    users = User.query.filter(or_(User.access == ACCESS[TEAM_CAPTAIN], User.access == ACCESS[TREASURER]))\
        .order_by(case({True: 0, False: 1}, value=User.is_active), User.team_id).all()
    teams = Team.query.all()
    organizer = db.session.query(User).filter(User.access == ACCESS[ORGANIZER]).first()
    return render_template('admin/user_list.html', data=data, users=users, teams=teams, organizer=organizer)


@bp.route('/organizer_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def organizer_account():
    organizer = db.session.query(User).filter(User.access == ACCESS[ORGANIZER]).first()
    if organizer is None:
        form = CreateOrganizerForm()
        if form.validate_on_submit():
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.set_password(form.password.data)
            user.access = ACCESS[ORGANIZER]
            user.send_messages_email = bool(form.send_email.data)
            db.session.add(user)
            db.session.commit()
            flash(f"Organizer account \"{user.username}\" created.", 'alert-success')
            return redirect(url_for('self_admin.user_list'))
    else:
        form = EditOrganizerForm()
        form.username.data = organizer.username
        form.email.data = organizer.email
        form.send_email.data = TF[organizer.send_new_messages_email]
        if form.validate_on_submit():
            organizer.email = form.email.data
            if form.password.data != '':
                organizer.set_password(form.password.data)
            organizer.send_messages_email = bool(form.send_email.data)
            db.session.commit()
            flash(f"Organizer account \"{organizer.username}\" updated.", 'alert-success')
            return redirect(url_for('self_admin.user_list'))
    return render_template('admin/organizer_account.html', form=form)


@bp.route('/create_team_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def create_team_account():
    form = CreateTeamForm()
    if form.validate_on_submit():
        team = Team()
        team.name = form.name.data
        team.city = form.city.data
        team.country = form.country.data
        db.session.add(team)
        db.session.commit()
        flash(f"Team {team.name} from {team.city}, {team.country} created.", 'alert-success')
        return redirect(url_for('self_admin.user_list'))
    return render_template('admin/team_account.html', form=form, edit=False)


@bp.route('/create_team_captain', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def create_team_captain():
    form = CreateTeamCaptainAccountForm()
    query = Team.query.filter(~exists().where(User.team))
    if len(query.all()) > 0:
        form.team.query = query
        if form.validate_on_submit():
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.set_password(form.password.data)
            user.access = ACCESS[TEAM_CAPTAIN]
            user.is_active = True
            user.send_messages_email = True
            db.session.add(user)
            treasurer = User()
            treasurer.username = form.username.data.replace("Teamcaptain", "Treasurer")
            treasurer.access = ACCESS[TREASURER]
            treasurer.is_active = False
            treasurer.send_messages_email = False
            db.session.add(treasurer)
            db.session.commit()
            flash(f"Team captain account \"{user.username}\" created.", 'alert-success')
            flash(f"Treasurer account \"{treasurer.username}\" created.", 'alert-success')
            return redirect(url_for('self_admin.user_list'))
    else:
        flash(f"There is no team without a team captain. Please create a new team first.", 'alert-warning')
        return redirect(url_for('self_admin.user_list'))
    return render_template('admin/team_captain.html', form=form, edit=False)


@bp.route('/debug_tools', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def debug_tools():
    form = request.args
    if 'force_error' in form:
        print(None.email)
    if len(form) > 0:
        return redirect(url_for('main.dashboard'))
    return render_template('admin/debug_tools.html')


@bp.route('/maintenance', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def maintenance():
    form = request.args
    if '502_page' in form:
        generate_maintenance_page()
    if 'maintenance_mode_on' in form:
        g.sc.website_accessible = False
        db.session.commit()
    if 'maintenance_mode_off' in form:
        g.sc.website_accessible = True
        db.session.commit()
    if len(form) > 0:
        return redirect(url_for('self_admin.maintenance'))
    return render_template('admin/maintenance.html')


def clear_tables():
    User.query.filter(User.access == ACCESS[DANCER]).delete()
    User.query.filter(User.access == ACCESS[SUPER_VOLUNTEER]).delete()
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        if table.name not in EXCLUDED_FROM_CLEARING:
            print('Cleared table {}.'.format(table))
            db.session.execute(table.delete())
            if not current_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:'):
                db.session.execute(f"ALTER TABLE {table.name} AUTO_INCREMENT = 1;")
    tf = Team.query.all()
    for f in tf:
        f.amount_paid = 0
    db.session.commit()


@bp.route('/test_populate', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
@requires_testing_environment
def test_populate():
    form = request.args
    if len(form) > 0:
        clear_tables()
        flash("Cleared tables.", "alert-success")
    if "NTDS2018ENSCHEDE" in form:
        populate_test_data("NTDS2018ENSCHEDE")
        flash("Populated with system with test data from the 2018 NTDS in Enschede.", "alert-success")
    if "ETDS2018BRNO" in form:
        populate_test_data("ETDS2018BRNO")
        flash("Populated with system with test data from the 2018 ETDS in Brno", "alert-success")
    if len(form) > 0:
        return redirect(url_for('self_admin.test_populate'))
    return render_template('admin/test_populate.html')
