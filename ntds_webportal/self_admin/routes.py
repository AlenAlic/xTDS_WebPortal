from flask import render_template, request, send_file
from ntds_webportal.self_admin import bp
from ntds_webportal.models import requires_access_level
from ntds_webportal.data import *
from instance.populate import TEAM_CAPTAINS
import xlsxwriter
from io import BytesIO


@bp.route('/debug_tools', methods=['GET', 'POST'])
@requires_access_level([ACCESS['admin']])
def debug_tools():
    if request.method == 'POST':
        form = request.form
        if 'force_error' in form:
            print(None.email)
    return render_template('admin/debug_tools.html')


@bp.route('/users_lists', methods=['GET', 'POST'])
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
