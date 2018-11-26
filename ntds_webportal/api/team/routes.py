from flask import jsonify
from flask_login import login_required
from ntds_webportal.models import requires_access_level, Team, Contestant, ContestantInfo, StatusInfo
from ntds_webportal.api import bp
from ntds_webportal.data import *
from sqlalchemy import or_


@bp.route('/team/guaranteed_dancers/<int:team_id>', methods=["GET"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def team_guaranteed_dancers(team_id):
    team = Team.query.filter(Team.team_id == team_id).first()
    dancers = Contestant.query.join(ContestantInfo, StatusInfo)\
        .filter(ContestantInfo.team == team, StatusInfo.status == REGISTERED,
                or_(ContestantInfo.team_captain.is_(True), StatusInfo.guaranteed_entry.is_(True))).all()
    return jsonify(len(dancers))


@bp.route('/team/confirmed_dancers/<int:team_id>', methods=["GET"])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
def team_confirmed_dancers(team_id):
    team = Team.query.filter(Team.team_id == team_id).first()
    dancers = Contestant.query.join(ContestantInfo, StatusInfo)\
        .filter(ContestantInfo.team == team, StatusInfo.status == CONFIRMED).all()
    return jsonify([d.to_dict() for d in dancers])
