from flask import render_template, request, redirect, url_for, flash, g, current_app, send_file
from flask_login import login_required, current_user, logout_user, login_user
from ntds_webportal import db
from ntds_webportal.self_admin import bp
from ntds_webportal.self_admin.forms import SwitchUserForm, CreateOrganizerForm, EditOrganizerForm, SystemSetupForm, \
    ResetOrganizerAccountForm
from ntds_webportal.models import requires_access_level, User, Team, SystemConfiguration, Contestant, \
    StatusInfo, AttendedPreviousTournamentContestant, NotSelectedContestant, EXCLUDED_FROM_CLEARING, \
    requires_testing_environment, Event, NameChangeRequest, PartnerRequest, ShiftSlot
from ntds_webportal.functions import str2bool, reset_tournament_state, \
    make_system_configuration_accessible_to_organizer, generate_maintenance_page
from ntds_webportal.auth.email import send_organizer_activation_email
from ntds_webportal.functions import random_password, active_teams, competing_teams
from ntds_webportal.data import *
from sqlalchemy import or_, case
import datetime
from test_data.test_populate import PAST_TOURNAMENTS, populate_test_data
import xlsxwriter
from io import BytesIO


@bp.route('/system_setup', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def system_setup():
    organizer = User.query.filter(User.access == ACCESS[ORGANIZER]).first()
    sc = SystemConfiguration.query.first()
    reset_organizer_account_form = ResetOrganizerAccountForm()
    if request.method == 'GET':
        reset_organizer_account_form.tournament.data = sc.tournament
        reset_organizer_account_form.year.data = sc.year
        reset_organizer_account_form.city.data = sc.city
        reset_organizer_account_form.username.data = f"{sc.tournament }{sc.city}{sc.year}"
    if request.method == 'POST':
        if "reset_organizer_account" in request.form:
            if reset_organizer_account_form.validate_on_submit():
                sc.tournament = reset_organizer_account_form.tournament.data
                sc.year = reset_organizer_account_form.year.data
                sc.city = reset_organizer_account_form.city.data
                tsd = datetime.datetime(reset_organizer_account_form.tournament_starting_date.data.year,
                                        reset_organizer_account_form.tournament_starting_date.data.month,
                                        reset_organizer_account_form.tournament_starting_date.data.day, 0, 0, 0, 0)
                sc.tournament_starting_date = tsd.replace(tzinfo=datetime.timezone.utc).timestamp()

                organizer.username = f"{reset_organizer_account_form.tournament.data}" \
                    f"{reset_organizer_account_form.city.data}{reset_organizer_account_form.year.data}"
                organizer.email = reset_organizer_account_form.email.data
                organizer_pass = random_password()
                organizer.set_password(organizer_pass)
                organizer.send_new_messages_email = True
                organizer.is_active = True
                assistants = User.query.filter(User.access > ACCESS[ORGANIZER], User.access < ACCESS[TEAM_CAPTAIN])\
                    .all()
                for assistant in assistants:
                    assistant.is_active = True
                    assistant.set_password(random_password())
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
        if 'reset_website' in request.form:
            NameChangeRequest.query.delete()
            PartnerRequest.query.delete()
            ShiftSlot.query.delete()
            User.query.filter(User.access > ACCESS[ADMIN], User.access < ACCESS[DANCER]).update({User.is_active: False})
            User.query.filter(User.access == ACCESS[TEAM_CAPTAIN]).update({User.activate: False})
            User.query.filter(User.access == ACCESS[TREASURER]).update({User.password_hash: None, User.email: None})
            Team.query.update({Team.amount_paid: 0})
            dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == CONFIRMED,
                                                               StatusInfo.checked_in.is_(True)).all()
            for dancer in dancers:
                check_attendee = AttendedPreviousTournamentContestant.query\
                    .filter(AttendedPreviousTournamentContestant.email == dancer.email.lower()).first()
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
            NotSelectedContestant.query.filter(NotSelectedContestant.tournament == g.sc.tournament).delete()
            dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == REGISTERED).all()
            for dancer in dancers:
                check_attendee = NotSelectedContestant.query\
                    .filter(NotSelectedContestant.email == dancer.email.lower()).first()
                if check_attendee is None:
                    attendee = NotSelectedContestant()
                    attendee.first_name = dancer.first_name
                    attendee.prefixes = dancer.prefixes
                    attendee.last_name = dancer.last_name
                    attendee.email = dancer.email.lower()
                    attendee.tournament = g.sc.tournament
                    db.session.add(attendee)
            db.session.commit()
            User.query.filter(User.access >= ACCESS[DANCER]).delete()
            reset_tournament_state()
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
            return redirect(url_for('main.dashboard'))
        if 'download_dancer_data' in request.form:
            pass
            dancers = Contestant.query.all()
            dancers = [d.dancer_excel_data() for d in dancers]
            header = {d: i for i, d in enumerate(dancers[0], 3)}
            fn = f'dancer_data_{g.sc.tournament}_{g.sc.city}_{g.sc.year}.xlsx'
            output = BytesIO()
            wb = xlsxwriter.Workbook(output, {'in_memory': True})
            f = wb.add_format({'text_wrap': True, 'bold': True})
            ws = wb.add_worksheet(name=datetime.date.today().strftime("%B %d, %Y"))
            for name, index in header.items():
                ws.write(0, index, name, f)
            ws.set_column(1, 2, 80)
            for i, d in enumerate(dancers, 1):
                for data in d:
                    ws.write(i, header[data], str(d[data]))
            wb.close()
            output.seek(0)
            return send_file(output, as_attachment=True, attachment_filename=fn)
    return render_template('admin/system_setup.html', roa_form=reset_organizer_account_form)


@bp.route('/system_configuration', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN], ACCESS[ORGANIZER]])
def system_configuration():
    form = SystemSetupForm()
    if request.method == 'GET':
        form.tournament.data = g.sc.tournament
        form.year.data = g.sc.year
        form.city.data = g.sc.city
        tsd = datetime.datetime.utcfromtimestamp(g.sc.tournament_starting_date).replace(tzinfo=datetime.timezone.utc)
        form.tournament_starting_date.data = datetime.date(tsd.year, tsd.month, tsd.day)

        form.main_page_link.data = g.sc.main_page_link
        form.terms_and_conditions_link.data = g.sc.terms_and_conditions_link
        form.merchandise_link.data = g.sc.merchandise_link

        form.number_of_teamcaptains.data = g.sc.number_of_teamcaptains
        form.additional_teamcaptain_large_teams.data = str(g.sc.additional_teamcaptain_large_teams)
        form.additional_teamcaptain_large_teams_cutoff.data = g.sc.additional_teamcaptain_large_teams_cutoff

        form.beginners_level.data = str(g.sc.beginners_level)
        form.closed_level.data = str(g.sc.closed_level)
        form.breitensport_obliged_blind_date.data = str(g.sc.breitensport_obliged_blind_date)
        form.salsa_competition.data = str(g.sc.salsa_competition)
        form.polka_competition.data = str(g.sc.polka_competition)

        form.student_price.data = g.sc.student_price
        form.non_student_price.data = g.sc.non_student_price
        form.phd_student_category.data = str(g.sc.phd_student_category)
        form.phd_student_price.data = g.sc.phd_student_price

        form.finances_refund.data = str(g.sc.finances_refund)
        form.finances_refund_percentage.data = g.sc.finances_refund_percentage
        frd = datetime.datetime.utcfromtimestamp(g.sc.finances_refund_date).replace(tzinfo=datetime.timezone.utc)
        frd += datetime.timedelta(days=-1)
        form.finances_refund_date.data = datetime.date(frd.year, frd.month, frd.day)

        form.first_time_ask.data = str(g.sc.first_time_ask)
        form.ask_adult.data = str(g.sc.ask_adult)
        form.ask_diet_allergies.data = str(g.sc.ask_diet_allergies)
        form.ask_volunteer.data = str(g.sc.ask_volunteer)
        form.ask_first_aid.data = str(g.sc.ask_first_aid)
        form.ask_emergency_response_officer.data = str(g.sc.ask_emergency_response_officer)
        form.ask_adjudicator_highest_achieved_level.data = str(g.sc.ask_adjudicator_highest_achieved_level)
        form.ask_adjudicator_certification.data = str(g.sc.ask_adjudicator_certification)
    if request.method == 'POST':
        if current_user.is_organizer():
            form.tournament.data = g.sc.tournament
            form.year.data = g.sc.year
            form.city.data = g.sc.city
            tsd = datetime.datetime.utcfromtimestamp(g.sc.tournament_starting_date)
            form.tournament_starting_date.data = datetime.date(tsd.year, tsd.month, tsd.day)
            if g.ts.main_raffle_result_visible:
                form.number_of_teamcaptains.data = g.sc.number_of_teamcaptains
                form.additional_teamcaptain_large_teams.data = str(g.sc.additional_teamcaptain_large_teams)
                form.additional_teamcaptain_large_teams_cutoff.data = g.sc.additional_teamcaptain_large_teams_cutoff
            if g.ts.registration_period_started:
                form.beginners_level.data = str(g.sc.beginners_level)
                form.closed_level.data = str(g.sc.closed_level)
                form.breitensport_obliged_blind_date.data = str(g.sc.breitensport_obliged_blind_date)
        if form.number_of_teamcaptains.data == 2:
            form.additional_teamcaptain_large_teams.data = str(g.sc.additional_teamcaptain_large_teams)
            form.additional_teamcaptain_large_teams_cutoff.data = g.sc.additional_teamcaptain_large_teams_cutoff
        if not str2bool(form.finances_refund.data):
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
            g.sc.merchandise_link = form.merchandise_link.data

            g.sc.number_of_teamcaptains = form.number_of_teamcaptains.data
            g.sc.additional_teamcaptain_large_teams = str2bool(form.additional_teamcaptain_large_teams.data)
            g.sc.additional_teamcaptain_large_teams_cutoff = form.additional_teamcaptain_large_teams_cutoff.data

            g.sc.beginners_level = str2bool(form.beginners_level.data)
            g.sc.closed_level = str2bool(form.closed_level.data)
            g.sc.breitensport_obliged_blind_date = str2bool(form.breitensport_obliged_blind_date.data)
            g.sc.salsa_competition = str2bool(form.salsa_competition.data)
            g.sc.polka_competition = str2bool(form.polka_competition.data)

            g.sc.student_price = form.student_price.data
            g.sc.non_student_price = form.non_student_price.data
            g.sc.phd_student_category = str2bool(form.phd_student_category.data)
            g.sc.phd_student_price = form.phd_student_price.data

            g.sc.finances_refund = str2bool(form.finances_refund.data)
            g.sc.finances_refund_percentage = form.finances_refund_percentage.data
            frd = datetime.datetime(form.finances_refund_date.data.year, form.finances_refund_date.data.month,
                                    form.finances_refund_date.data.day, 3, 0, 0, 0) + datetime.timedelta(days=1)
            g.sc.finances_refund_date = frd.replace(tzinfo=datetime.timezone.utc).timestamp()

            g.sc.first_time_ask = str2bool(form.first_time_ask.data)
            g.sc.ask_adult = str2bool(form.ask_adult.data)
            g.sc.ask_diet_allergies = str2bool(form.ask_diet_allergies.data)
            g.sc.ask_volunteer = str2bool(form.ask_volunteer.data)
            g.sc.ask_first_aid = str2bool(form.ask_first_aid.data)
            g.sc.ask_emergency_response_officer = str2bool(form.ask_emergency_response_officer.data)
            g.sc.ask_adjudicator_highest_achieved_level = str2bool(form.ask_adjudicator_highest_achieved_level.data)
            g.sc.ask_adjudicator_certification = str2bool(form.ask_adjudicator_certification.data)

            db.session.commit()
            flash("Configuration saved.", "alert-success")
            db.session.commit()
            if current_user.is_organizer():
                g.ts.system_configured = True
                return redirect(url_for('main.dashboard'))
            return redirect(url_for('self_admin.system_configuration'))
    return render_template('admin/system_configuration.html', form=form)


@bp.route('/switch_user', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def switch_user():
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
    if request.method == "POST":
        if dancer_super_volunteer_form.submit.name in request.form:
            if dancer_super_volunteer_form.validate_on_submit():
                user = User.query.filter(User.user_id == dancer_super_volunteer_form.user.data).first()
                if user is not None:
                    logout_user()
                    login_user(user)
                else:
                    flash('User account is not active.')
                return redirect(url_for('main.index'))
    teams = {team: f"{team.name}.png" if team.country == NETHERLANDS else "generic.png" for team in active_teams()}
    return render_template('admin/switch_user.html', dancer_super_volunteer_form=dancer_super_volunteer_form,
                           teams=teams)


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


@bp.route('/switch_to_team_captain/<int:team_id>', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def switch_to_team_captain(team_id):
    user = User.query.join(Team).filter(User.is_active.is_(True), User.access == ACCESS[TEAM_CAPTAIN],
                                        Team.team_id == team_id).first()
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
    users = User.query.filter(or_(User.access == ACCESS[TEAM_CAPTAIN], User.access == ACCESS[TREASURER])) \
        .order_by(case({True: 0, False: 1}, value=User.is_active), User.team_id).all()
    teams = competing_teams().all()
    organizer = db.session.query(User).filter(User.access == ACCESS[ORGANIZER]).first()
    return render_template('admin/user_list.html', users=users, teams=teams, organizer=organizer)


@bp.route('/organizer_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN]])
def organizer_account():
    organizer = db.session.query(User).filter(User.access == ACCESS[ORGANIZER]).first()
    if organizer is None:
        form = CreateOrganizerForm()
        if form.validate_on_submit():
            if request.method == "POST":
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
        if request.method == "POST":
            if form.validate_on_submit():
                organizer.email = form.email.data
                if form.password.data != '':
                    organizer.set_password(form.password.data)
                organizer.send_messages_email = bool(form.send_email.data)
                db.session.commit()
                flash(f"Organizer account \"{organizer.username}\" updated.", 'alert-success')
                return redirect(url_for('self_admin.user_list'))
    return render_template('admin/organizer_account.html', form=form)


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
    NameChangeRequest.query.delete()
    PartnerRequest.query.delete()
    ShiftSlot.query.delete()
    User.query.filter(User.access == ACCESS[DANCER]).delete()
    User.query.filter(User.access == ACCESS[SUPER_VOLUNTEER]).delete()
    User.query.filter(User.access >= ACCESS[ORGANIZER]).update({User.activate: False, User.is_active: False})
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
    if request.method == "POST":
        if "clear_tables" in request.form:
            clear_tables()
            flash("Cleared tables.", "alert-success")
        if "test_data" in request.form:
            clear_tables()
            populate_test_data(request.form["test_data"])
            flash(f"Populated with system with test data from {request.form['test_data']} tournament.", "alert-success")
        return redirect(url_for('main.dashboard'))
    return render_template('admin/test_populate.html', past_tournaments=PAST_TOURNAMENTS)


# @bp.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# @requires_access_level([ACCESS[ADMIN]])
# def dashboard():
#     return render_template('admin/dashboard.html')
