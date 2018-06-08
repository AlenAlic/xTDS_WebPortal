from flask import render_template, request
from ntds_webportal.self_admin import bp
from ntds_webportal.models import requires_access_level
from ntds_webportal.data import *


@bp.route('/debug_tools', methods=['GET', 'POST'])
@requires_access_level([ACCESS['admin']])
def debug_tools():
    if request.method == 'POST':
        form = request.form
        if 'force_error' in form:
            print(None.email)
    return render_template('admin/debug_tools.html')
