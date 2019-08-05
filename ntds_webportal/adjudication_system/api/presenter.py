from flask import jsonify, Response
from flask_login import login_required
from ntds_webportal.models import Competition, DancingClass, Round, requires_access_level, requires_tournament_state
from ntds_webportal.adjudication_system.api import bp
from ntds_webportal.data import *


@login_required
@requires_access_level([ACCESS[PRESENTER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
@bp.route('/presenter/competition_list', methods=["GET"])
def presenter_competition_list():
    competitions = Competition.query.join(DancingClass).filter(DancingClass.name != TEST)\
        .order_by(Competition.when).all()
    if len(competitions) > 0:
        return jsonify({i: {"id": c.competition_id, "name": c.name(), 'date': c.when}
                        for i, c in enumerate(competitions)})
    return Response(status=204)


@login_required
@requires_access_level([ACCESS[PRESENTER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
@bp.route('/presenter/competition/<int:competition_id>/rounds', methods=["GET"])
def presenter_competition_rounds(competition_id):
    competition = Competition.query.get_or_404(competition_id)
    if competition is not None:
        if competition.dancing_class.name != TEST:
            return jsonify(competition.presenter_rounds())
    return Response(status=204)


@login_required
@requires_access_level([ACCESS[PRESENTER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
@bp.route('/presenter/round/<int:round_id>/adjudicators', methods=["GET"])
def presenter_round_adjudicators(round_id):
    r = Round.query.get_or_404(round_id)
    if r is not None:
        if r.competition.dancing_class.name != TEST:
            return jsonify(r.presenter_adjudicators())
    return Response(status=204)


@login_required
@requires_access_level([ACCESS[PRESENTER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
@bp.route('/presenter/round/<int:round_id>/starting_list', methods=["GET"])
def presenter_round(round_id):
    r = Round.query.get_or_404(round_id)
    if r is not None:
        if r.competition.dancing_class.name != TEST:
            return jsonify(r.starting_list())
    return Response(status=204)


@login_required
@requires_access_level([ACCESS[PRESENTER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
@bp.route('/presenter/round/<int:round_id>/couples_present', methods=["GET"])
def presenter_round_couples_present(round_id):
    r = Round.query.get_or_404(round_id)
    if r is not None:
        if r.competition.dancing_class.name != TEST:
            return jsonify(r.couples_present())
    return Response(status=204)


@login_required
@requires_access_level([ACCESS[PRESENTER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
@bp.route('/presenter/round/<int:round_id>/no_redance_couples', methods=["GET"])
def presenter_round_no_redance_couples(round_id):
    r = Round.query.get_or_404(round_id)
    if r is not None:
        if r.competition.dancing_class.name != TEST:
            return jsonify(r.presenter_no_redance_couples())
    return Response(status=204)


@login_required
@requires_access_level([ACCESS[PRESENTER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
@bp.route('/presenter/round/<int:round_id>/final_results', methods=["GET"])
def presenter_round_no_final_results(round_id):
    r = Round.query.get_or_404(round_id)
    if r is not None:
        if r.competition.dancing_class.name != TEST and r.is_final():
            x = r.skating_summary()
            return jsonify(None)
    return Response(status=204)
