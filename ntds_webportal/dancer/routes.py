from flask import render_template, url_for, redirect, flash, g, request
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.dancer import bp
from ntds_webportal.teamcaptains.forms import EditContestantForm
from ntds_webportal.models import requires_access_level
from ntds_webportal.dancer.forms import FeedbackForm
from ntds_webportal.data import *
import datetime


@bp.route('/dancer_data', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[DANCER]])
def dancer_data():
    dancer = current_user.dancer
    feedback_form = FeedbackForm()
    form = EditContestantForm(dancer)
    if request.method == GET:
        form.populate(dancer)
        if dancer.status_info.feedback_about_information is not None:
            feedback_form.feedback.data = dancer.status_info.feedback_about_information
    if 'privacy_checkbox' in request.values:
        flash('Privacy policy accepted.', 'alert-success')
        dancer.status_info.set_status(REGISTERED)
        db.session.commit()
        return redirect(url_for('url_dancer.dancer_data'))
    if feedback_form.validate_on_submit():
        flash('Feedback sent to team captain.', 'alert-success')
        dancer.status_info.feedback_about_information = feedback_form.feedback.data
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('dancer/dancer_data.html', dancer=dancer, form=form, sc=g.sc, feedback_form=feedback_form,
                           timestamp=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())
