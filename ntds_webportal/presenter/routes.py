from flask import render_template
from flask_login import login_required
from ntds_webportal.presenter import bp
from ntds_webportal.models import requires_access_level, requires_tournament_state
from ntds_webportal.data import *


@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[PRESENTER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def dashboard():
    return render_template('presenter/dashboard.html')
