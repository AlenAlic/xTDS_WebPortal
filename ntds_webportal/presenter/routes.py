from flask import render_template
from flask_login import login_required
from ntds_webportal.presenter import bp
from ntds_webportal.models import requires_access_level, requires_tournament_state
from ntds_webportal.data import *


# TODO
# Is a couple present on the floor DONE
# Who is dancing this round DONE
# Who qualified for a class (ABOVE)
# Adjudicator location DONE
# Publish heat list to app
# Automatically cross couple if they are on the floor for the next heat
# Redance: who doesn't have to dance DONE
# Final: Name(s), number(s), team(s) DONE
# Final results: Name(s), number(s), team(s), placings, result of all dances
# Points Lion


@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[PRESENTER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def dashboard():
    return render_template('presenter/dashboard.html')

