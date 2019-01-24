from flask import jsonify, request
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import requires_access_level, Contestant
from ntds_webportal.api import bp
from ntds_webportal.data import *


@bp.route('/contestants/<int:contestant_id>', methods=["GET"])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    return jsonify(dancer.to_dict())


@bp.route('/contestants/<int:contestant_id>/status_info/guaranteed_entry', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_status_info_guaranteed_entry(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.status_info.guaranteed_entry = not dancer.status_info.guaranteed_entry
        db.session.commit()
    return jsonify(dancer.to_dict())


@bp.route('/contestants/<int:contestant_id>/status_info/checked_in', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_status_info_checked_in(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.status_info.checked_in = not dancer.status_info.checked_in
        db.session.commit()
    return jsonify(dancer.to_dict())


@bp.route('/contestants/<int:contestant_id>/status_info/received_starting_number', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_status_info_received_starting_number(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.status_info.received_starting_number = not dancer.status_info.received_starting_number
        db.session.commit()
    return jsonify(dancer.to_dict())


@bp.route('/contestants/<int:contestant_id>/merchandise_info/merchandise_received', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_merchandise_info_merchandise_received(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.merchandise_info.merchandise_received = not dancer.merchandise_info.merchandise_received
        db.session.commit()
    return jsonify(dancer.to_dict())


@bp.route('/contestants/<int:contestant_id>/payment_info/all_paid', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_payment_info_all_paid(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.payment_info.all_paid(not dancer.payment_info.all_paid())
        db.session.commit()
    return jsonify(dancer.to_dict())


@bp.route('/contestants/<int:contestant_id>/payment_info/merchandise_paid', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_payment_info_merchandise_paid(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.payment_info.merchandise_paid(not dancer.payment_info.merchandise_paid())
        db.session.commit()
    return jsonify(dancer.to_dict())
