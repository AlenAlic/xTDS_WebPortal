from flask import jsonify, request
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import Round, DanceActive
from ntds_webportal.adjudication_system.api import bp


@bp.route('/to/round/<int:round_id>', methods=["GET", "PATCH"])
@login_required
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
def to_toggle_round_dance(round_id, dance_id):
    dancing_round = Round.query.get_or_404(round_id)
    dance = DanceActive.query.filter(DanceActive.round == dancing_round, DanceActive.dance_id == dance_id)\
        .first_or_404()
    if request.method == "PATCH":
        dancing_round.is_active = True
        dance.is_active = not dance.is_active
        db.session.commit()
    return jsonify(dance.is_active)