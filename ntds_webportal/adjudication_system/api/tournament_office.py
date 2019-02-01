from flask import jsonify, request, render_template
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import Round, DanceActive, requires_access_level
from ntds_webportal.adjudication_system.api import bp
from ntds_webportal.data import *


@bp.route('/to/round/<int:round_id>', methods=["GET", "PATCH"])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def to_toggle_round(round_id):
    dancing_round = Round.query.get_or_404(round_id)
    if request.method == "PATCH":
        dancing_round.is_active = not dancing_round.is_active
        for dance in dancing_round.dance_active:
            dance.is_active = dancing_round.is_active
        db.session.commit()
    return jsonify(dancing_round.is_active)


@bp.route('/to/round/<int:round_id>/dance/<int:dance_id>', methods=["GET", "PATCH"])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def to_toggle_round_dance(round_id, dance_id):
    dancing_round = Round.query.get_or_404(round_id)
    dance = DanceActive.query.filter(DanceActive.round == dancing_round, DanceActive.dance_id == dance_id)\
        .first_or_404()
    if request.method == "PATCH":
        dancing_round.is_active = True
        dance.is_active = not dance.is_active
        db.session.commit()
    return jsonify(dance.is_active)


@bp.route('/to/publish_heat_list/<int:round_id>', methods=["POST", "DELETE"])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def to_publish_heat_list(round_id):
    dancing_round = Round.query.get_or_404(round_id)
    if request.method == "POST":
        if not dancing_round.is_final():
            dancing_round.competition.heat_list = render_template('adjudication_system/heat_list.html',
                                                                  dancing_round=dancing_round).replace('\n', '')
            db.session.commit()
            return jsonify(True)
    if request.method == "DELETE":
        dancing_round.competition.heat_list = None
        db.session.commit()
        return jsonify(False)
    return jsonify(False)
