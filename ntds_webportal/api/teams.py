from flask import jsonify
from flask_login import login_required
from ntds_webportal.models import requires_access_level, Team
from ntds_webportal.api import bp
from ntds_webportal.data import *


@bp.route('/teams/<int:team_id>/guaranteed_dancers', methods=["GET"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def team_guaranteed_dancers(team_id):
    return jsonify([d.to_dict() for d in Team.query.get(team_id).guaranteed_dancers()])


@bp.route('/teams/<int:team_id>/confirmed_dancers', methods=["GET"])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
def team_confirmed_dancers(team_id):
    return jsonify([d.to_dict() for d in Team.query.get(team_id).confirmed_dancers()])


@bp.route('/teams/<int:team_id>/cancelled_dancers_with_merchandise', methods=["GET"])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
def team_cancelled_dancers_with_merchandise(team_id):
    return jsonify([d.to_dict() for d in Team.query.get(team_id).cancelled_dancers_with_merchandise()])
