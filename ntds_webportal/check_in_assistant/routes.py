from flask import render_template, g, jsonify
from flask_login import login_required
from ntds_webportal.check_in_assistant import bp
from ntds_webportal.models import requires_access_level, requires_tournament_state
from ntds_webportal.data import *
from ntds_webportal.functions import active_teams


@bp.route('/tournament_check_in', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def tournament_check_in():
    teams = [{
        'team_id': team.team_id,
        'team_name': team.display_name(),
        "prices": g.sc.entry_fee_prices()
    } for team in active_teams() if len(team.confirmed_dancers()) > 0]
    return render_template('check_in_assistant/tournament_check_in.html', teams=teams)
