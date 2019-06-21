from flask import jsonify, request, json
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import requires_access_level, Contestant, MerchandisePurchase, Refund
from ntds_webportal.api import bp
from ntds_webportal.data import *


@bp.route('/contestants/<int:contestant_id>/status_info/guaranteed_entry', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_status_info_guaranteed_entry(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.status_info.guaranteed_entry = not dancer.status_info.guaranteed_entry
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/check_in/<bool:check_in>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN], ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_check_in(contestant_id, check_in):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.status_info.checked_in = check_in
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/entry_payment/<bool:entry_paid>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN], ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_entry_payment(contestant_id, entry_paid):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.payment_info.entry_paid = entry_paid
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/all_payment/<bool:all_paid>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN], ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_all_payment(contestant_id, all_paid):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.payment_info.all_is_paid(all_paid)
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/merchandise_payment/<int:merchandise_purchased_id>/'
          '<bool:merchandise_paid>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN], ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_merchandise_payment(contestant_id, merchandise_purchased_id, merchandise_paid):
    dancer = Contestant.query.get_or_404(contestant_id)
    purchase = MerchandisePurchase.query.get_or_404(merchandise_purchased_id)
    if request.method == "PATCH":
        purchase.paid = merchandise_paid
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/merchandise_received/<int:merchandise_purchased_id>/'
          '<bool:merchandise_received>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN], ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
def contestants_merchandise_received(contestant_id, merchandise_purchased_id, merchandise_received):
    dancer = Contestant.query.get_or_404(contestant_id)
    purchase = MerchandisePurchase.query.get_or_404(merchandise_purchased_id)
    if request.method == "PATCH":
        purchase.received = merchandise_received
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/give_entry_fee_refund', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def contestants_give_entry_fee_refund(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.payment_info.give_entry_fee_refund()
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/remove_payment_requirement', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def contestants_remove_payment_requirement(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        dancer.status_info.remove_payment_requirement()
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/purchase_ordered/<int:merchandise_purchased_id>/<bool:ordered>',
          methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def contestants_purchase_ordered(contestant_id, merchandise_purchased_id, ordered):
    dancer = Contestant.query.get_or_404(contestant_id)
    purchase = MerchandisePurchase.query.get_or_404(merchandise_purchased_id)
    if request.method == "PATCH":
        purchase.ordered = ordered
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/give_general_refund', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def contestants_give_general_refund(contestant_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    data = json.loads(request.data)
    if request.method == "PATCH":
        refund = Refund()
        refund.reason = data["reason"]
        refund.amount = int(data["amount"])
        refund.payment_info = dancer.payment_info
        db.session.add(refund)
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/update_refund/<int:refund_id>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def contestants_update_refund(contestant_id, refund_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    refund = Refund.query.get_or_404(refund_id)
    data = json.loads(request.data)
    if request.method == "PATCH":
        refund.reason = data["reason"]
        refund.amount = int(data["amount"])
        db.session.commit()
    return jsonify(dancer.json())


@bp.route('/contestants/<int:contestant_id>/delete_refund/<int:refund_id>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def contestants_delete_refund(contestant_id, refund_id):
    dancer = Contestant.query.get_or_404(contestant_id)
    refund = Refund.query.get_or_404(refund_id)
    if request.method == "PATCH":
        db.session.delete(refund)
        db.session.commit()
    return jsonify(dancer.json())
