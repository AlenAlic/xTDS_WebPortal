from flask import jsonify, request, json
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import requires_access_level, Team
from ntds_webportal.api import bp
from ntds_webportal.data import *


@bp.route('/teams/update_received_amount', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def team_update_received_amount():
    amounts = json.loads(request.data)
    teams = Team.query.filter(Team.team_id.in_(amounts.keys())).all()
    for team in teams:
        team.amount_paid = amounts[str(team.team_id)]
    db.session.commit()
    return jsonify(amounts)


@bp.route('/teams/<int:team_id>/guaranteed_dancers', methods=["GET"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def team_guaranteed_dancers(team_id):
    return jsonify([d.json() for d in Team.query.get(team_id).guaranteed_dancers()])


@bp.route('/teams/<int:team_id>/check_in_dancers', methods=["GET"])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
def team_check_in_dancers(team_id):
    team = Team.query.get(team_id)
    return jsonify({d.contestant_id: d.json() for d in team.check_in_dancers()})


@bp.route('/teams/<int:team_id>/confirmed_dancers', methods=["GET"])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
def team_confirmed_dancers(team_id):
    return jsonify({d.contestant_id: d.json() for d in Team.query.get(team_id).confirmed_dancers()})


@bp.route('/teams/<int:team_id>/cancelled_dancers_with_merchandise', methods=["GET"])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
def team_cancelled_dancers_with_merchandise(team_id):
    return jsonify([d.json() for d in Team.query.get(team_id).cancelled_dancers_with_merchandise()])
