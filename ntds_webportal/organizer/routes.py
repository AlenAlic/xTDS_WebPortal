from flask import render_template, request, flash, redirect, url_for, send_file, g, Markup
from flask_login import login_required, logout_user, login_user
from ntds_webportal import db
from ntds_webportal.organizer import bp
from ntds_webportal.models import requires_access_level, Team, Contestant, ContestantInfo, DancingInfo,\
    StatusInfo, AdditionalInfo, NameChangeRequest, User, MerchandiseInfo, TournamentState, \
    SalsaPartners, PolkaPartners, VolunteerInfo, requires_tournament_state, SuperVolunteer
from ntds_webportal.functions import submit_updated_dancing_info, get_dancing_categories, random_password
from ntds_webportal.organizer.forms import NameChangeResponse, ChangeEmailForm, FinalizeMerchandiseForm
from ntds_webportal.self_admin.forms import CreateBaseUserWithoutEmailForm, EditAssistantAccountForm
from ntds_webportal.organizer.email import send_registration_open_email, send_gdpr_reminder_email
from ntds_webportal.teamcaptains.forms import EditDancingInfoForm
from ntds_webportal.auth.email import send_team_captain_activation_email
from ntds_webportal.helper_classes import TeamFinancialOverview
from ntds_webportal.teamcaptains.forms import EditContestantForm
from ntds_webportal.volunteering.forms import SuperVolunteerForm
import ntds_webportal.data as data
from ntds_webportal.data import *
from sqlalchemy import or_, case
import xlsxwriter
from io import BytesIO, StringIO
import datetime


@bp.route('/user_list', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def user_list():
    form = request.args
    if 'activate_teamcaptains' in form:
        team_captains = User.query.join(Team).filter(User.access == ACCESS[TEAM_CAPTAIN])\
            .order_by(case({True: 0, False: 1}, value=User.is_active), User.team_id)
        if g.sc.tournament == NTDS:
            team_captains = team_captains.filter(Team.country == NETHERLANDS).all()
        else:
            team_captains = team_captains.all()
        for tc in team_captains:
            if tc.email is not None:
                tc.is_active = True
                tc_pass = random_password()
                tc.set_password(tc_pass)
                send_team_captain_activation_email(tc.email, tc, tc_pass,
                                                   tournament=g.sc.tournament, year=g.sc.year, city=g.sc.city)
        g.ts.website_accessible_to_teamcaptains = True
        db.session.commit()
        message = "The accounts for all team captains{} have been activated.<br/><br/>" \
                  "An e-mail has been sent to all team captains with the login credentials."
        if g.sc.tournament == NTDS:
            message = message.format(f" from {NETHERLANDS}")
        flash(Markup(message), "alert-success")
    if len(form) > 0:
        return redirect(url_for('main.dashboard'))
    if not g.ts.website_accessible_to_teamcaptains:
        users = User.query.join(Team).filter(User.access == ACCESS[TEAM_CAPTAIN]).order_by(User.team_id, User.user_id)
    else:
        users = User.query.join(Team)\
            .filter(or_(User.access == ACCESS[TEAM_CAPTAIN], User.access == ACCESS[TREASURER])) \
            .order_by(case({True: 0, False: 1}, value=User.is_active), User.team_id, User.user_id)
    if g.sc.tournament == NTDS:
        users = users.filter(Team.country == NETHERLANDS).all()
    else:
        users = users.all()
    bda = db.session.query(User).filter(User.access == ACCESS[BLIND_DATE_ASSISTANT]).first()
    chi = db.session.query(User).filter(User.access == ACCESS[CHECK_IN_ASSISTANT]).first()
    ada = db.session.query(User).filter(User.access == ACCESS[ADJUDICATOR_ASSISTANT]).first()
    return render_template('organizer/user_list.html', data=data, users=users, bda=bda, chi=chi, ada=ada)


def assistant_account(access_level):
    submit = False
    user = db.session.query(User).filter(User.access == ACCESS[access_level]).first()
    if user is None:
        form = CreateBaseUserWithoutEmailForm()
        if access_level == BLIND_DATE_ASSISTANT:
            form.username.data = BLIND_DATE_ASSISTANT_ACCOUNT_NAME
        elif access_level == CHECK_IN_ASSISTANT:
            form.username.data = CHECK_IN_ASSISTANT_ACCOUNT_NAME
        elif access_level == ADJUDICATOR_ASSISTANT:
            form.username.data = ADJUDICATOR_ASSISTANT_ACCOUNT_NAME
        if form.validate_on_submit():
            user = User()
            user.username = form.username.data
            user.set_password(form.password.data)
            user.access = ACCESS[access_level]
            user.is_active = True
            user.send_new_messages_email = False
            db.session.add(user)
            db.session.commit()
            flash(f"Assistant account \"{user.username}\" created.", 'alert-success')
            submit = True
    else:
        form = EditAssistantAccountForm()
        form.username.data = user.username
        if form.validate_on_submit():
            if form.password.data != '':
                user.set_password(form.password.data)
                db.session.commit()
                flash(f"Assistant account \"{user.username}\" updated.", 'alert-success')
            else:
                flash(f"No changes were made to save.", "alert-warning")
            submit = True
    return form, user, submit


@bp.route('/blind_date_assistant_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def blind_date_assistant_account():
    form, user, submit = assistant_account(BLIND_DATE_ASSISTANT)
    if submit:
        return redirect(url_for('organizer.user_list'))
    return render_template('organizer/assistant_account.html', data=data, form=form, user=user,
                           assistant=BLIND_DATE_ASSISTANT)


@bp.route('/check_in_assistant_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def check_in_assistant_account():
    form, user, submit = assistant_account(CHECK_IN_ASSISTANT)
    if submit:
        return redirect(url_for('organizer.user_list'))
    return render_template('organizer/assistant_account.html', data=data, form=form, user=user,
                           assistant=CHECK_IN_ASSISTANT)


@bp.route('/adjudicator_assistant_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def adjudicator_assistant_account():
    form, user, submit = assistant_account(ADJUDICATOR_ASSISTANT)
    if submit:
        return redirect(url_for('organizer.user_list'))
    return render_template('organizer/assistant_account.html', data=data, form=form, user=user,
                           assistant=ADJUDICATOR_ASSISTANT)


@bp.route('/change_email/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def change_email(number):
    user = User.query.filter(User.user_id == number).first()
    form = ChangeEmailForm()
    if request.method == 'GET':
        form.email.data = user.email
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.commit()
        flash(f"Changed e-mail of {user.username} to {form.email.data}.", 'alert-success')
        return redirect(url_for('organizer.user_list'))
    return render_template('admin/change_email.html', form=form, user=user)


@bp.route('/registration_management', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(TEAM_CAPTAINS_HAVE_ACCESS)
def registration_management():
    no_gdpr_dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == NO_GDPR)\
        .order_by(Contestant.first_name).all()
    form = request.args
    if 'start_registration_period' in form:
        g.ts.registration_period_started = True
        g.ts.registration_open = True
        g.sc.system_configuration_accessible = False
        team_captains = User.query.filter(User.access == ACCESS[TEAM_CAPTAIN], User.is_active.is_(True)).all()
        for tc in team_captains:
            send_registration_open_email(tc.email)
        admin = User.query.filter(User.access == ACCESS[ADMIN]).first()
        send_registration_open_email(admin.email)
        flash(f"Registration for the {g.sc.tournament} has started!", "alert-success")
    if 'close_registration' in form:
        g.ts.registration_open = False
        flash(f"Registration for the {g.sc.tournament} has been closed.", "alert-info")
    if 'open_registration' in form:
        g.ts.registration_open = True
        flash(f"Registration for the {g.sc.tournament} has been opened again.", "alert-info")
    if 'notify_no_gdpr' in form:
        for dancer in no_gdpr_dancers:
            send_gdpr_reminder_email(dancer)
        flash(f"Reminder for accepting the privacy policy has been sent to the dancers in question.", "alert-info")
    if len(form) > 0:
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('organizer/registration_management.html', no_gdpr_dancers=no_gdpr_dancers)


@bp.route('/registration_overview', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def registration_overview():
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .order_by(ContestantInfo.team_id,
                  case({CONFIRMED: 0, SELECTED: 1, REGISTERED: 2, CANCELLED: 3}, value=StatusInfo.status),
                  Contestant.first_name).all()
    all_teams = db.session.query(Team).all()
    dancers = [{'country': team.country, 'name': team.name, 'id': team.city,
                'dancers': len(Contestant.query.join(ContestantInfo).filter(ContestantInfo.team == team)
                               .order_by(Contestant.first_name).all())} for team in all_teams]
    # dancers = [d for d in dancers if len(d['dancers']) > 0]
    dutch_dancers = [team for team in dancers if team['country'] == NETHERLANDS]
    german_dancers = [team for team in dancers if team['country'] == GERMANY]
    other_dancers = [team for team in dancers if team['country'] != NETHERLANDS and team['country'] != GERMANY]
    return render_template('organizer/registration_overview.html', data=data, all_dancers=all_dancers,
                           dutch_dancers=dutch_dancers, german_dancers=german_dancers, other_dancers=other_dancers)


@bp.route('/view_dancer/<int:number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def view_dancer(number):
    dancer = Contestant.query.filter(Contestant.contestant_id == number).first()
    form = EditContestantForm()
    form.organizer_populate(dancer)
    return render_template('organizer/view_dancer.html', dancer=dancer, form=form,
                           timestamp=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())


@bp.route('/name_change_list', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def name_change_list():
    nml_open = NameChangeRequest.query.filter(NameChangeRequest.state == NameChangeRequest.STATE['Open']).all()
    nml_closed = NameChangeRequest.query.filter(NameChangeRequest.state != NameChangeRequest.STATE['Open']).all()
    return render_template('organizer/name_change_list.html', nml_open=nml_open, nml_closed=nml_closed)


@bp.route('/name_change_respond/<req>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
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


@bp.route('/dancing_info_list', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[BLIND_DATE_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def dancing_info_list():
    dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(or_(StatusInfo.status == CONFIRMED, StatusInfo.status == SELECTED))\
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    return render_template('organizer/dancing_info_list.html', data=data, dancers=dancers)


@bp.route('/edit_dancing_info/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[BLIND_DATE_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def edit_dancing_info(number):
    dancer = db.session.query(Contestant).join(DancingInfo).filter(Contestant.contestant_id == number).first()
    form = EditDancingInfoForm(dancer)
    if request.method == GET:
        form.populate(dancer)
    if request.method == POST:
        form.custom_validate()
    if form.validate_on_submit():
        flash('{} data has been changed successfully.'.format(submit_updated_dancing_info(form, contestant=dancer)),
              'alert-success')
        return redirect(url_for('organizer.dancing_info_list'))
    return render_template('organizer/edit_dancing_info.html', data=data, form=form, dancer=dancer)


@bp.route('/finances_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def finances_overview():
    # WISH - Discuss with "Penny" for what to add - downloads for total page and summary pages
    all_teams = db.session.query(Team)
    if g.sc.tournament == NTDS:
        all_teams = all_teams.filter(Team.country == NETHERLANDS).all()
    else:
        all_teams = all_teams.all()
    if request.method == 'POST':
        if 'submit' in request.form:
            changes = False
            for team in all_teams:
                amount_paid = request.form.get(str(team.team_id))
                if amount_paid != ''.strip() and amount_paid is not None:
                    amount_paid = int(round(float(amount_paid)*100))
                    if team.amount_paid != amount_paid:
                        team.amount_paid = amount_paid
                        changes = True
            if changes:
                db.session.commit()
                flash('Changes saved successfully.', 'alert-success')
            else:
                flash('No changes were made to submit.', 'alert-warning')
            return redirect(url_for('organizer.finances_overview'))
    all_confirmed_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.payment_required.is_(True), StatusInfo.status == CONFIRMED)\
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    all_cancelled_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(StatusInfo.payment_required.is_(True), StatusInfo.status == CANCELLED) \
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    teams = [{'team': team, 'id': team.city,
              'confirmed_dancers': [dancer for dancer in all_confirmed_dancers if
                                    dancer.contestant_info.team.name == team.name],
              'cancelled_dancers': [dancer for dancer in all_cancelled_dancers if
                                    dancer.contestant_info.team.name == team.name],
              'finances': TeamFinancialOverview(
                  User.query.filter(User.team == team, User.access == ACCESS[TEAM_CAPTAIN]).first())
              .finances_overview()}
             for team in all_teams]
    teams = [team for team in teams if (len(team['confirmed_dancers']) + len(team['cancelled_dancers'])) > 0]
    for t in teams:
        if g.sc.finances_full_refund:
            t['refund_dancers'] = [d for d in t['cancelled_dancers'] if d.payment_info.full_refund]
        if g.sc.finances_partial_refund:
            t['refund_dancers'] = [d for d in t['cancelled_dancers'] if d.payment_info.partial_refund]
    dutch_teams = [team for team in teams if team['team'].country == NETHERLANDS]
    german_teams = [team for team in teams if team['team'].country == GERMANY]
    other_teams = [team for team in teams if
                   team['team'].country != NETHERLANDS and team['team'].country != GERMANY]
    return render_template('organizer/finances_overview.html', teams=teams, data=data,
                           dutch_teams=dutch_teams, german_teams=german_teams, other_teams=other_teams)


@bp.route('/remove_payment_requirement/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def remove_payment_requirement(number):
    dancer = StatusInfo.query.filter(StatusInfo.contestant_id == number).first()
    dancer.remove_payment_requirement()
    return redirect(url_for('organizer.finances_overview'))


@bp.route('/merchandise', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def merchandise():
    current_timestamp = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    form = FinalizeMerchandiseForm()
    if form.is_submitted() and form.validate_on_submit():
        if not g.ts.merchandise_finalized:
            registered_dancers = Contestant.query.join(StatusInfo)\
                .filter(or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR,
                            StatusInfo.status == CANCELLED)).all()
            registered_dancers = [d for d in registered_dancers if d.merchandise_info.ordered_merchandise()]
            for dancer in registered_dancers:
                dancer.merchandise_info.cancel_merchandise()
            g.ts.merchandise_finalized = True
            flash("Merchandise finalized.", "alert-success")
            db.session.commit()
    dancers = Contestant.query.join(StatusInfo).join(ContestantInfo).join(AdditionalInfo).join(MerchandiseInfo)\
        .join(Team).filter(or_(StatusInfo.status == CONFIRMED, StatusInfo.status == CANCELLED))\
        .order_by(Team.city, Contestant.first_name).all()
    dancers = [dancer for dancer in dancers if dancer.merchandise_info.ordered_merchandise()]
    shirts = {shirt_size: 0 for shirt_size in SHIRT_SIZES}
    mugs, bags = 0, 0
    for dancer in dancers:
        try:
            shirts[dancer.merchandise_info.t_shirt] += 1
        except KeyError:
            pass
        mugs += 1 if dancer.merchandise_info.mug else 0
        bags += 1 if dancer.merchandise_info.bag else 0
    shirts = {SHIRT_SIZES[shirt]: quantity for shirt, quantity in shirts.items()}
    total_shirts = sum([quantity for size, quantity in shirts.items()])
    download = request.args
    if 'download_file' in download:
        header = {'Name': 0, 'E-mail': 1, 'Team': 2}
        base_len = len(header)
        for i in range(0, 3):
            if g.sc.merchandise_sold(i):
                header.update({g.sc.merchandise_name(i): len(header)})
        fn = f'merchandise_{g.sc.tournament}_{g.sc.city}_{g.sc.year}.xlsx'
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        f = wb.add_format({'text_wrap': True, 'bold': True})
        ws = wb.add_worksheet(name=datetime.date.today().strftime("%B %d, %Y"))
        for name, index in header.items():
            ws.write(0, index, name, f)
        ws.set_column(0, 0, 30)
        ws.set_column(1, 1, 40)
        ws.set_column(2, 3, 20)
        for d in range(0, len(dancers)):
            ws.write(d + 1, 0, dancers[d].get_full_name())
            ws.write(d + 1, 1, dancers[d].email)
            ws.write(d + 1, 2, dancers[d].contestant_info.team.city)
            for i in range(base_len, len(header)):
                counter = base_len
                if g.sc.t_shirt_sold:
                    try:
                        ws.write(d + 1, counter, SHIRT_SIZES[dancers[d].merchandise_info.t_shirt])
                    except KeyError:
                        ws.write(d + 1, counter, NONE)
                    counter += 1
                if g.sc.mug_sold:
                    ws.write(d + 1, counter, TF[dancers[d].merchandise_info.mug])
                    counter += 1
                if g.sc.bag_sold:
                    ws.write(d + 1, counter, TF[dancers[d].merchandise_info.bag])
                    counter += 1
        ws.freeze_panes(1, 0)
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename=fn)
    return render_template('organizer/merchandise.html', dancers=dancers, current_timestamp=current_timestamp,
                           form=form, shirts=shirts, total_shirts=total_shirts, mugs=mugs, bags=bags)


@bp.route('/sleeping_hall', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def sleeping_hall():
    team_captains = db.session.query(User).filter(User.access == ACCESS[TEAM_CAPTAIN], User.is_active.is_(True))\
        .order_by(User.username).all()
    teams = [{'city': team_captain.team.city,
              'number_of_dancers': db.session.query(Contestant).join(ContestantInfo, StatusInfo, AdditionalInfo)
             .filter(ContestantInfo.team == team_captain.team, StatusInfo.status == CONFIRMED,
                     AdditionalInfo.sleeping_arrangements.is_(True)).count()} for team_captain in team_captains]
    super_volunteers = SuperVolunteer.query.filter(SuperVolunteer.sleeping_arrangements.is_(True)).all()
    total = sum([team['number_of_dancers'] for team in teams]) + len(super_volunteers)
    form = request.args
    if 'download_file' in form:
        fn = f'sleeping_hall_{g.sc.tournament}_{g.sc.city}_{g.sc.year}.xlsx'
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        f = wb.add_format({'text_wrap': True, 'bold': True})
        la = wb.add_format({'align': 'left'})
        ws = wb.add_worksheet()
        ws.write(0, 0, 'Team', f)
        ws.write(0, 1, 'People in sleeping hall (Total: {total})'.format(total=total), f)
        for d in range(0, len(teams)):
            ws.write(d + 1, 0, teams[d]['city'])
            ws.write(d + 1, 1, teams[d]['number_of_dancers'], la)
        ws.write(len(teams) + 1, 0, 'Super Volunteers')
        ws.write(len(teams) + 1, 1, super_volunteers, la)
        ws.set_column(0, 0, 30)
        ws.set_column(1, 1, 40)
        ws.freeze_panes(1, 0)
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename=fn)
    return render_template('organizer/sleeping_hall.html', teams=teams, super_volunteers=super_volunteers, total=total)


@bp.route('/view_super_volunteer/<int:number>', methods=[GET])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def view_super_volunteer(number):
    super_volunteer = SuperVolunteer.query.filter(SuperVolunteer.volunteer_id == number).first()
    form = SuperVolunteerForm()
    form.populate(super_volunteer)
    return render_template('organizer/view_super_volunteer.html', form=form)


@bp.route('/diet_allergies', methods=[GET, POST])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def diet_allergies():
    # PRIORITY Remove comma separated on input
    dancers = Contestant.query.join(ContestantInfo, StatusInfo).filter(StatusInfo.status == CONFIRMED,
                                                                       ContestantInfo.diet_allergies != "").all()
    dancers = [d for d in dancers if d.contestant_info.diet_allergies.strip() != ""
               and d.contestant_info.diet_allergies != "-"]
    people = [{'id': 'd-' + str(d.contestant_id), 'name': d.get_full_name(), 'diet': d.contestant_info.diet_allergies,
               'notes': d.contestant_info.organization_diet_notes} for d in dancers]
    super_volunteers = SuperVolunteer.query.filter(SuperVolunteer.diet_allergies != "").all()
    super_volunteers = [sv for sv in super_volunteers if sv.diet_allergies.strip() != "" and sv.diet_allergies != "-"]
    people.extend([{'id': 'sv-' + str(sv.volunteer_id), 'name': sv.get_full_name(), 'diet': sv.diet_allergies,
                    'notes': sv.organization_diet_notes} for sv in super_volunteers])
    people.sort(key=lambda x: x['name'])
    old_notes = [p['notes'] for p in people if p['notes'].strip() != ""]
    all_confirmed_dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == CONFIRMED).all()
    all_super_volunteers = SuperVolunteer.query.all()
    total = len(all_confirmed_dancers) + len(all_super_volunteers)
    no_special_diet = total - len(people)
    form = request.args
    if 'download_file' in form:
        fn = f'diet_allergies_{g.sc.tournament}_{g.sc.city}_{g.sc.year}.xlsx'
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        f = wb.add_format({'text_wrap': True, 'bold': True})
        ws = wb.add_worksheet()
        ws.write(0, 0, 'Who?', f)
        ws.write(0, 1, 'Diet/Allergies (Total: {total})'.format(total=len(people)), f)
        for p in range(0, len(people)):
            ws.write(p + 1, 0, people[p]['name'])
            ws.write(p + 1, 1, people[p]['diet'])
        ws.set_column(0, 0, 30)
        ws.set_column(1, 1, 80)
        ws.freeze_panes(1, 0)
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename=fn)
    if request.method == 'POST':
        if 'submit' in request.form:
            changes = False
            for p in people:
                diet_notes = request.form.get(p['id'])
                if p['id'].split('-')[0] == "d":
                    person = ContestantInfo.query.get(int(p['id'].split('-')[1]))
                else:
                    person = SuperVolunteer.query.get(int(p['id'].split('-')[1]))
                if person.organization_diet_notes != diet_notes:
                    person.organization_diet_notes = diet_notes
                    changes = True
            if changes:
                db.session.commit()
                flash('Changes saved successfully.', 'alert-success')
            else:
                flash('No changes were made to submit.', 'alert-warning')
            return redirect(url_for('organizer.diet_allergies'))
    return render_template('organizer/diet_allergies.html',
                           people=people, total=total, no_special_diet=no_special_diet, old_notes=old_notes)


@bp.route('/adjudicators_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[ADJUDICATOR_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def adjudicators_overview():
    # PRIORITY - Add Super Volunteers
    # LONG TERM - Completely new system - Print login sheets - schedule available on personal page - assignment system
    ts = TournamentState.query.first()
    ballroom_adjudicators = Contestant.query.join(VolunteerInfo, StatusInfo, ContestantInfo, DancingInfo)\
        .filter(StatusInfo.status == CONFIRMED, VolunteerInfo.jury_ballroom != NO)\
        .order_by(case({YES: 0, MAYBE: 1, NO: 2}, value=VolunteerInfo.jury_ballroom), ContestantInfo.team_id)\
        .all()
    latin_adjudicators = Contestant.query.join(VolunteerInfo, StatusInfo, ContestantInfo, DancingInfo) \
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
        fn = 'adjudicators_{g.sc.tournament}_{g.sc.city}_{g.sc.year}.xlsx'
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        f = wb.add_format({'text_wrap': True, 'bold': True})
        adjudicators = {BALLROOM: ballroom_adjudicators, LATIN: latin_adjudicators, SALSA: salsa_adjudicators,
                        POLKA: polka_adjudicators}
        for comp, adj in adjudicators.items():
            ws = wb.add_worksheet(name=comp)
            ws.write(0, 0, 'Dancer', f)
            ws.write(0, 1, 'Team', f)
            ws.write(0, 2, 'E-mail', f)
            ws.write(0, 3, 'Wants to adjudicate?', f)
            if comp == BALLROOM or comp == LATIN:
                ws.write(0, 4, 'Has license?', f)
                ws.write(0, 5, 'Highest achieved level', f)
                ws.write(0, 6, 'Dancing Ballroom?', f)
                ws.write(0, 7, 'Dancing Latin?', f)
                ws.set_column(0, 7, 30)
                for d in range(0, len(adj)):
                    ws.write(d + 1, 0, adj[d].get_full_name())
                    ws.write(d + 1, 1, adj[d].contestant_info.team.name)
                    ws.write(d + 1, 2, adj[d].email)
                    if comp == BALLROOM:
                        wants_to = adj[d].volunteer_info.jury_ballroom
                        lic = adj[d].volunteer_info.license_jury_ballroom
                        lvl = adj[d].volunteer_info.level_ballroom
                    else:
                        wants_to = adj[d].volunteer_info.jury_latin
                        lic = adj[d].volunteer_info.license_jury_latin
                        lvl = adj[d].volunteer_info.level_latin
                    ws.write(d + 1, 3, wants_to)
                    ws.write(d + 1, 4, lic)
                    ws.write(d + 1, 5, lvl)
                    dc = get_dancing_categories(adj[d].dancing_info)
                    ws.write(d + 1, 6, dc[BALLROOM].level)
                    ws.write(d + 1, 7, dc[LATIN].level)
            else:
                ws.set_column(0, 3, 30)
                for d in range(0, len(adj)):
                    ws.write(d + 1, 0, adj[d].get_full_name())
                    ws.write(d + 1, 1, adj[d].contestant_info.team.name)
                    ws.write(d + 1, 2, adj[d].email)
                    if comp == SALSA:
                        wants_to = adj[d].volunteer_info.jury_salsa
                    else:
                        wants_to = adj[d].volunteer_info.jury_polka
                    ws.write(d + 1, 3, wants_to)
            ws.freeze_panes(1, 0)
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename=fn)
    return render_template('organizer/adjudicators_overview.html', ts=ts, data=data,
                           ballroom_adjudicators=ballroom_adjudicators, latin_adjudicators=latin_adjudicators,
                           salsa_adjudicators=salsa_adjudicators, polka_adjudicators=polka_adjudicators)


@bp.route('/BAD', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def bad():
    # PRIORITY - Update (see mail to Marek)
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
        registered_dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == REGISTERED).all()
        text = render_template('organizer/_BAD_createTournament.sql', teams=teams, dancers=dancers,
                               registered_dancers=registered_dancers)
        output = StringIO(text)
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="createTournament.sql")
    if 'download_populateCouples' in form:
        leads = Contestant.query.join(StatusInfo).join(DancingInfo) \
            .filter(or_(StatusInfo.status == SELECTED, StatusInfo.status == CONFIRMED), DancingInfo.role == LEAD) \
            .all()
        leads = [di for lead in leads for di in lead.dancing_info if di.role == LEAD and di.partner is not None]
        closed_open_leads = Contestant.query.join(StatusInfo).join(DancingInfo) \
            .filter(or_(StatusInfo.status == SELECTED, StatusInfo.status == CONFIRMED), DancingInfo.role == LEAD,
                    or_(DancingInfo.level == CLOSED, DancingInfo.level == OPEN_CLASS)).all()
        closed_open_leads = [di for lead in closed_open_leads for di in lead.dancing_info if di.role == LEAD
                             and (di.level == CLOSED or di.level == OPEN_CLASS)]
        closed_open_follows = Contestant.query.join(StatusInfo).join(DancingInfo) \
            .filter(or_(StatusInfo.status == SELECTED, StatusInfo.status == CONFIRMED), DancingInfo.role == FOLLOW,
                    or_(DancingInfo.level == CLOSED, DancingInfo.level == OPEN_CLASS)).all()
        closed_open_follows = [di for follow in closed_open_follows for di in follow.dancing_info if di.role == FOLLOW
                               and (di.level == CLOSED or di.level == OPEN_CLASS)]
        salsa_couples = SalsaPartners.query.all()
        polka_couples = PolkaPartners.query.all()
        text = render_template('organizer/_BAD_populateCouples.sql', leads=leads,
                               salsa_couples=salsa_couples, polka_couples=polka_couples,
                               closed_open_leads=closed_open_leads, closed_open_follows=closed_open_follows)
        output = StringIO(text)
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="populateCouples.sql")
    return render_template('organizer/BAD.html', ts=g.ts)


@bp.route('/switch_to_bda', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def switch_to_bda():
    bda = User.query.filter(User.access == ACCESS[BLIND_DATE_ASSISTANT]).first()
    if bda is not None:
        logout_user()
        login_user(bda)
    else:
        flash('Blind Date Assistant account not created.')
    return redirect(url_for('main.index'))


@bp.route('/switch_to_cia', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def switch_to_cia():
    cia = User.query.filter(User.access == ACCESS[CHECK_IN_ASSISTANT]).first()
    if cia is not None:
        logout_user()
        login_user(cia)
    else:
        flash('Check-in Assistant account not created.')
    return redirect(url_for('main.index'))


@bp.route('/switch_to_ada', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def switch_to_ada():
    ada = User.query.filter(User.access == ACCESS[ADJUDICATOR_ASSISTANT]).first()
    if ada is not None:
        logout_user()
        login_user(ada)
    else:
        flash('Adjudicator Assistant account not created.')
    return redirect(url_for('main.index'))
