from flask import render_template
from flask_login import login_required
from ntds_webportal.check_in_assistant import bp
from ntds_webportal.models import requires_access_level, requires_tournament_state
from ntds_webportal.data import *
from ntds_webportal.functions import active_teams
from ntds_webportal.api.teams import team_confirmed_dancers


@bp.route('/tournament_check_in', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def tournament_check_in():
    teams = active_teams()
    teams = [{'team_id': team.team_id, 'name': team.name,
              'dancers': team_confirmed_dancers(team.team_id).json} for team in teams]
    return render_template('check_in_assistant/tournament_check_in.html', teams=teams)
