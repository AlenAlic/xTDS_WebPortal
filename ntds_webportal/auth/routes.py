from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from ntds_webportal import db
from ntds_webportal.auth import bp
from ntds_webportal.auth.forms import ResetPasswordRequestForm, ResetPasswordForm
from ntds_webportal.models import User
from ntds_webportal.auth.email import send_password_reset_email


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password.')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    if user == 'error':
        flash('Not a valid token.', 'alert-danger')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'alert-success')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form, user=user)
