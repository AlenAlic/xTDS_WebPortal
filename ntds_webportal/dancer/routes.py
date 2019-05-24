from flask import render_template, url_for, redirect, flash, g, request
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.dancer import bp
from ntds_webportal.teamcaptains.forms import EditContestantForm
from ntds_webportal.models import requires_access_level, MerchandiseItem, MerchandiseItemVariant, MerchandisePurchase
from ntds_webportal.dancer.forms import FeedbackForm, BuyMerchandiseForm
from ntds_webportal.data import *


@bp.route('/dancer_data', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[DANCER]])
def dancer_data():
    dancer = current_user.dancer
    feedback_form = FeedbackForm()
    form = EditContestantForm(dancer)
    if request.method == "GET":
        form.populate(dancer)
        if dancer.status_info.feedback_about_information is not None:
            feedback_form.feedback.data = dancer.status_info.feedback_about_information
    if request.method == "POST":
        if 'privacy_submit' in request.form:
            dancer.status_info.set_status(REGISTERED)
            db.session.commit()
            flash('Privacy policy accepted.', 'alert-success')
            if g.sc.merchandise():
                flash('You can now order merchandise from the Merchandise tab on the dashboard.', 'alert-primary')
            return redirect(url_for('url_dancer.dancer_data'))
        if 'submit_dancer_feedback' in request.form and feedback_form.validate_on_submit():
            flash('Feedback sent to team captain.', 'alert-success')
            dancer.status_info.feedback_about_information = feedback_form.feedback.data
            db.session.commit()
            return redirect(url_for('main.dashboard'))
    return render_template('dancer/dancer_data.html', dancer=dancer, feedback_form=feedback_form)


@bp.route('/merchandise', methods=['GET', "POST"])
@login_required
@requires_access_level([ACCESS[DANCER]])
def merchandise():
    all_merchandise = MerchandiseItem.query.all()
    variants = {m.merchandise_item_id: [v.merchandise_item_variant_id for v in m.variants] for m in all_merchandise}
    variants.update({0: []})
    form = BuyMerchandiseForm()
    if request.method == "POST":
        if form.submit.name in request.form:
            if not g.ts.merchandise_finalized:
                if form.validate_on_submit():
                    variant = MerchandiseItemVariant.query\
                        .filter(MerchandiseItemVariant.merchandise_item_variant_id == form.variant.data).first()
                    purchase = MerchandisePurchase(merchandise_info=current_user.dancer.merchandise_info,
                                                   merchandise_item_variant=variant)
                    current_user.dancer.merchandise_info.purchases.append(purchase)
                    db.session.commit()
                    flash(f"{purchase} has been ordered.")
                    return redirect(url_for('url_dancer.merchandise'))
        if "cancel" in request.form:
            purchase = MerchandisePurchase.query\
                .filter(MerchandisePurchase.merchandise_purchased_id == request.form["cancel"]).first()
            purchase.cancel(show_flash_messages=True)
            return redirect(url_for('url_dancer.merchandise'))
    return render_template('dancer/merchandise.html', variants=variants, form=form)
