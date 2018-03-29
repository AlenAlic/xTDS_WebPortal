from flask import render_template, url_for, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from ntds_webportal import db
from ntds_webportal.main import bp
from ntds_webportal.models import User, TournamentState
from ntds_webportal.auth.forms import LoginForm, ChangePasswordForm


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'alert-danger')
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
    if current_user.is_tc():
        state = TournamentState.query.first()
        raffle_config = state.get_raffle_config()
        teamcaptain_page_accessible = current_user.has_dancers_registered()
        num_teamcaptains = current_user.teamcaptains_selected()
        return render_template('dashboard.html', state=state, max_tc=raffle_config['max_teamcaptains'],
                               teamcaptain_page_accessible=teamcaptain_page_accessible,
                               num_teamcaptains=num_teamcaptains)
    return render_template('dashboard.html')


@bp.route('/todo')
@login_required
def todo():
    return render_template('todo.html', title='#TODO')


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if not user.check_password(form.current_password.data):
            flash('Invalid username or password', 'alert-danger')
            return redirect(url_for('main.profile'))
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been changed.', 'alert-success')
        return redirect(url_for('main.index'))
    if current_user.is_tc():
        return redirect(url_for('teamcaptains.teamcaptain_profile'))
    else:
        return render_template('profile.html', form=form)
