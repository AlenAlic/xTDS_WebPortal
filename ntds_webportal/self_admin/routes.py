from flask import render_template, request, send_file, redirect, url_for, current_app, flash
from flask_login import login_required, current_user, logout_user, login_user
from ntds_webportal import db
from ntds_webportal.self_admin import bp
from ntds_webportal.self_admin.forms import SwitchUserForm, CreateBaseUserWithoutEmailForm, \
    CreateOrganizerForm, EditOrganizerForm, EditAssistantAccountForm, CreateTeamForm, \
    CreateTeamCaptainAccountForm
from ntds_webportal.models import requires_access_level, User, Team, TeamFinances
from ntds_webportal.data import *
import ntds_webportal.data as data
from instance.populate import TEAM_CAPTAINS
from sqlalchemy import or_, case, exists
import xlsxwriter
from io import BytesIO
import os


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
        team_finances = TeamFinances()
        team_finances.team = team
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
@requires_access_level([ACCESS['admin']])
def debug_tools():
    if request.method == 'POST':
        form = request.form
        if 'force_error' in form:
            print(None.email)
    return render_template('admin/debug_tools.html')


@bp.route('/maintenance', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['admin']])
def maintenance():
    form = request.args
    if '502_page' in form:
        maintenance_page = render_template('errors/502.html')
        dir_path = os.path.join(current_app.static_folder, '502.html')
        with open(dir_path, 'w') as the_file:
            the_file.write(maintenance_page)
    return render_template('admin/maintenance.html')


@bp.route('/switch_user', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['admin']])
def switch_user():
    form = SwitchUserForm()
    users = User.query.filter(User.is_active.is_(True), User.user_id != current_user.user_id).all()
    form.user.choices = map(lambda user: (user.user_id, user.username), users)
    if form.validate_on_submit():
        user = User.query.filter(User.user_id == form.user.data).first()
        logout_user()
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('admin/switch_user.html', form=form)


@bp.route('/users_lists', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ADMIN], ACCESS[ORGANIZER]])
def users_lists():
    fn = 'login_tc.xlsx'
    output = BytesIO()
    wb = xlsxwriter.Workbook(output, {'in_memory': True})
    ws = wb.add_worksheet(name='Teamcaptain Login Information')
    ws.write(0, 0, 'Team')
    ws.write(0, 1, 'Email')
    ws.write(0, 2, 'Username')
    ws.write(0, 3, 'Default Password')
    ws.write(0, 4, 'Password')
    teamcaptains = User.query.filter(User.access == ACCESS[TEAM_CAPTAIN], User.is_active.is_(True)).all()
    for index, tc in enumerate(teamcaptains):
        ws.write(index + 1, 0, tc.team.name)
        ws.write(index + 1, 1, tc.email)
        ws.write(index + 1, 2, tc.username)
        for default in TEAM_CAPTAINS:
            if default['username'] == tc.username:
                ws.write(index + 1, 3, default['password'])
                if tc.check_password(default['password']):
                    ws.write(index + 1, 4, 'Using default password')
                else:
                    ws.write(index + 1, 4, 'Using own password from last tournament.')
    ws.set_column(0, 0, 20)
    ws.set_column(1, 1, 40)
    ws.set_column(2, 2, 30)
    ws.set_column(3, 3, 20)
    ws.set_column(4, 4, 20)
    wb.close()
    output.seek(0)
    return send_file(output, as_attachment=True, attachment_filename=fn)
