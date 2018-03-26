from flask import render_template, url_for, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from ntds_webportal import db
from ntds_webportal.main import bp
from ntds_webportal.auth.forms import LoginForm, ChangePasswordForm, TreasurerForm
from ntds_webportal.models import User


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.index'))
        login_user(user)
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title='Home', login_form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been changed.')
        return redirect(url_for('main.index'))
    if current_user.is_tc():
        treasurer_form = TreasurerForm()
        return render_template('tc_profile.html', form=form, treasurer_form=treasurer_form)
    return render_template('profile.html', form=form)
