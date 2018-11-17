from flask import render_template, url_for, redirect, flash, g, request
from flask_login import current_user, login_user, login_required, logout_user
from ntds_webportal import db
from ntds_webportal.main import bp
from ntds_webportal.models import User
from ntds_webportal.auth.forms import LoginForm, ChangePasswordForm, SendEmailForNotificationsForm


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
        if not user.is_admin() and not g.sc.website_accessible:
            flash('The xTDS WebPortal is currently being prepared for the next tournament.'
                  'All accounts are temporarily disabled.')
            return render_template('inactive.html', title='Inactive', login_form=form)
        if user.is_active:
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash("Your account is currently inactive. It will become active again when the next tournament starts.")
            return redirect(url_for('main.index'))
    if not g.sc.website_accessible:
        return render_template('inactive.html', title='Inactive', login_form=form)
    return render_template('index.html', title='Home', login_form=form)


@bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.is_treasurer():
        if g.ts.main_raffle_result_visible:
            return redirect(url_for('teamcaptains.edit_finances'))
        else:
            return redirect(url_for('teamcaptains.treasurer_inaccessible'))
    if current_user.is_dancer():
        return render_template('dashboard.html', dancer=current_user.dancer)
    return render_template('dashboard.html')


@bp.route('/todo', methods=['GET'])
@login_required
def todo():
    # ADMIN
    # LONG TERM - Change so that teams and team captain/treasurer accounts are made at the same time
    # WISH - Make "Tournament" section in system setup throw warnings when doing something stupid

    # ORGANIZER
    # NEXT TOURNAMENT - Allow organizer to select what team captain to activate
    # NEXT TOURNAMENT - Allow organizer to enable/disable accounts
    return render_template('todo.html', title='#TODO')


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePasswordForm()
    send_email_form = SendEmailForNotificationsForm()
    if request.method == 'GET':
        send_email_form.send_email.data = current_user.send_new_messages_email
    if send_email_form.validate_on_submit():
        current_user.send_new_messages_email = send_email_form.send_email.data
        db.session.commit()
        flash('E-mail notification preference changed.', 'alert-success')
        return redirect(url_for('main.profile'))
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if not user.check_password(form.current_password.data):
            flash('Invalid username or password', 'alert-danger')
            return redirect(url_for('main.profile'))
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been changed.', 'alert-success')
        return redirect(url_for('main.profile'))
    if current_user.is_tc():
        return redirect(url_for('teamcaptains.teamcaptain_profile'))
    else:
        return render_template('profile.html', form=form, send_email_form=send_email_form)
