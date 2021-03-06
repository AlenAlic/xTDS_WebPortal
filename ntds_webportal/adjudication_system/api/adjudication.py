from flask import jsonify, request
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import Mark, Round, Adjudicator, Dance, FinalPlacing, requires_adjudicator_access_level
from ntds_webportal.adjudication_system.api import bp


@bp.route('/round/<int:round_id>/adjudicator/<int:adjudicator_id>/dance/<int:dance_id>', methods=["GET"])
@login_required
@requires_adjudicator_access_level
def adjudicator_round(round_id, adjudicator_id, dance_id):
    dancing_round = Round.query.get_or_404(round_id)
    adjudicator = Adjudicator.query.get_or_404(adjudicator_id)
    dance = Dance.query.get_or_404(dance_id)
    return jsonify(dancing_round.adjudicator_dance_to_dict(adjudicator, dance))


@bp.route('/mark/<int:mark_id>/mark', methods=["GET", "PATCH"])
@login_required
@requires_adjudicator_access_level
def mark_mark(mark_id):
    mark = Mark.query.get_or_404(mark_id)
    if request.method == "PATCH":
        if mark.heat.round.is_dance_active(mark.heat.dance):
            mark.mark = not mark.mark
            mark.notes = 0
            db.session.commit()
    return jsonify(mark.to_dict())


@bp.route('/mark/<int:mark_id>/notes', methods=["GET", "PATCH"])
@login_required
@requires_adjudicator_access_level
def mark_notes(mark_id):
    mark = Mark.query.get_or_404(mark_id)
    if request.method == "PATCH":
        if mark.heat.round.is_dance_active(mark.heat.dance):
            if not mark.mark:
                mark.notes += 1
                mark.notes = mark.notes % 4
            else:
                mark.notes = 0
            db.session.commit()
    return jsonify(mark.to_dict())


@bp.route('/final_placing/<int:final_placing_id>/final_placing/<int:place>', methods=["GET", "PATCH"])
@login_required
@requires_adjudicator_access_level
def final_placing_final_placing(final_placing_id, place):
    placing = FinalPlacing.query.get_or_404(final_placing_id)
    if request.method == "PATCH":
        if placing.round.is_dance_active(placing.dance):
            placings = FinalPlacing.query.filter(FinalPlacing.adjudicator == placing.adjudicator,
                                                 FinalPlacing.round == placing.round,
                                                 FinalPlacing.dance == placing.dance).all()
            if place < placing.final_placing:
                placing.final_placing = place
                if place > 0:
                    place_to_update = place
                    placings_to_update = [p for p in placings if p.final_placing == place_to_update
                                          and p.couple != placing.couple]
                    while len(placings_to_update) > 0 and place_to_update != 0:
                        place_to_update = (place_to_update + 1) % (len(placing.round.couples) + 1)
                        placings_to_update[0].final_placing = place_to_update
                        placings_to_update = [p for p in placings if p.final_placing == place_to_update
                                              and p.couple != placings_to_update[0].couple]
                db.session.commit()
            elif place > placing.final_placing:
                placing.final_placing = place
                if place > 0:
                    place_to_update = place
                    placings_to_update = [p for p in placings if p.final_placing == place_to_update
                                          and p.couple != placing.couple]
                    while len(placings_to_update) > 0 and place_to_update != 0:
                        place_to_update = (place_to_update - 1) % (len(placing.round.couples) + 1)
                        placings_to_update[0].final_placing = place_to_update
                        placings_to_update = [p for p in placings if p.final_placing == place_to_update
                                              and p.couple != placings_to_update[0].couple]
                db.session.commit()
    return jsonify(placing.to_dict())
