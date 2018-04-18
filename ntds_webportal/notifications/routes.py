from flask import render_template, url_for, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from ntds_webportal import db
from ntds_webportal.notifications import bp
from ntds_webportal.models import Notification
from ntds_webportal.auth.forms import LoginForm, ChangePasswordForm, TreasurerForm


@bp.route('/list')
@login_required
def list():
    notifications = Notification.query.filter_by(user=current_user, archived=False)\
        .order_by(Notification.unread.desc()).all()
    return render_template('notifications/list.html', title="Notifications", notifications=notifications)
