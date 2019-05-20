from flask import jsonify, request
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import requires_access_level, Contestant, MerchandisePurchase
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


@bp.route('/contestants/<int:contestant_id>/give_refund/<bool:give_refund>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def contestants_give_refund(contestant_id, give_refund):
    dancer = Contestant.query.get_or_404(contestant_id)
    if request.method == "PATCH":
        if give_refund:
            dancer.payment_info.set_refund()
        else:
            dancer.payment_info.remove_refund()
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
