from flask import render_template, url_for, redirect, flash
from ntds_webportal.main import bp
from flask_login import current_user, login_user, login_required, logout_user
from ntds_webportal.auth.forms import LoginForm
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
    return render_template('index.html', title='Home', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')
