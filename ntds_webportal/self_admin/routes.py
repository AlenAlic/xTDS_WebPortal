from flask import render_template, request, send_file, redirect, url_for, current_app
from flask_login import login_required, current_user, logout_user, login_user
from ntds_webportal.self_admin import bp
from ntds_webportal.self_admin.forms import SwitchUserForm
from ntds_webportal.models import requires_access_level, User
from ntds_webportal.data import *
from instance.populate import TEAM_CAPTAINS
import xlsxwriter
from io import BytesIO
import os


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
@requires_access_level([ACCESS['admin']])
def users_lists():
    fn = 'login_tc.xlsx'
    teamcaptains_sorted = sorted(TEAM_CAPTAINS, key=lambda k: k['city'])
    teamcaptains_sorted = [tc for tc in teamcaptains_sorted if tc['email'] is not None]
    output = BytesIO()
    wb = xlsxwriter.Workbook(output, {'in_memory': True})
    ws = wb.add_worksheet(name='Teamcaptain Login Information')
    ws.write(0, 0, 'City')
    ws.write(0, 1, 'Email')
    ws.write(0, 2, 'Username')
    ws.write(0, 3, 'Password')
    for c in range(0, len(teamcaptains_sorted)):
        ws.write(c+1, 0, teamcaptains_sorted[c]['city'])
        ws.write(c+1, 1, teamcaptains_sorted[c]['email'])
        ws.write(c+1, 2, teamcaptains_sorted[c]['username'])
        ws.write(c+1, 3, teamcaptains_sorted[c]['password'])
    ws.set_column(0, 0, 20)
    ws.set_column(1, 1, 40)
    ws.set_column(2, 2, 30)
    ws.set_column(3, 3, 20)
    wb.close()
    output.seek(0)
    return send_file(output, as_attachment=True, attachment_filename=fn)
