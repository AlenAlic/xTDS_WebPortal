from flask import jsonify, Response
from ntds_webportal.models import Competition, DancingClass
from ntds_webportal.adjudication_system.api import bp
from ntds_webportal.data import *


@bp.route('/app/competition_list', methods=["GET"])
def app_competition_list():
    competitions = Competition.query.join(DancingClass).filter(DancingClass.name != TEST)\
        .order_by(Competition.when).all()
    if len(competitions) > 0:
        return jsonify({i: {"id": c.competition_id, "name": c.name()} for i, c in enumerate(competitions)})
    return Response(status=204)


@bp.route('/app/competition_heat_list/<int:competition_id>', methods=["GET"])
def app_competition_heat_list(competition_id):
    competition = Competition.query.get(competition_id)
    if competition is not None:
        if competition.dancing_class.name != TEST and competition.heat_list is not None:
            return competition.heat_list
    return Response(status=204)
