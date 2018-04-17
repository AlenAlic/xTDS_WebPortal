from flask import render_template, url_for, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from ntds_webportal import db
from ntds_webportal.notifications import bp
from ntds_webportal.models import User
from ntds_webportal.auth.forms import LoginForm, ChangePasswordForm, TreasurerForm


@bp.route('/list')
def list():
    return render_template('todo.html', title="Notifications")