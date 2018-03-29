from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_user, login_required, logout_user
from ntds_webportal import db
from ntds_webportal.main import bp
from ntds_webportal.models import User, Team, Contestant, ContestantInfo, DancingInfo, VolunteerInfo, AdditionalInfo
from ntds_webportal.auth.forms import LoginForm, ChangePasswordForm, TreasurerForm
from ntds_webportal.auth.email import random_password, send_treasurer_activation_email
from ntds_webportal.main.forms import ContestantForm
from ntds_webportal.data import ACCESS, NO, LEAD, FOLLOW, CHOOSE


def contestant_validate_dancing(form):
    if form.ballroom_partner.data is not None:
        dancing_partner = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo) \
            .filter(ContestantInfo.number == form.ballroom_partner.data.contestant_info[0].number).first()
        if form.ballroom_role.data == dancing_partner.dancing_info[0].ballroom_role:
            if form.ballroom_role.data == LEAD:
                form.ballroom_role.data = 'same_role_lead'
            elif form.ballroom_role.data == FOLLOW:
                form.ballroom_role.data = 'same_role_follow'
        if form.ballroom_level.data != dancing_partner.dancing_info[0].ballroom_level:
            if dancing_partner.dancing_info[0].ballroom_level is None:
                form.ballroom_level.data = 'diff_levels_no_level'
            elif form.ballroom_level.data != CHOOSE:
                form.ballroom_level.data = 'diff_levels'
    if form.latin_partner.data is not None:
        dancing_partner = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo) \
            .filter(ContestantInfo.number == form.latin_partner.data.contestant_info[0].number).first()
        if form.latin_role.data == dancing_partner.dancing_info[0].latin_role:
            if form.latin_role.data == LEAD:
                form.latin_role.data = 'same_role_lead'
            elif form.latin_role.data == FOLLOW:
                form.latin_role.data = 'same_role_follow'
        if form.latin_level.data != dancing_partner.dancing_info[0].latin_level:
            if dancing_partner.dancing_info[0].latin_level is None:
                form.latin_level.data = 'diff_levels_no_level'
            elif form.latin_level.data != CHOOSE:
                form.latin_level.data = 'diff_levels'
    return form


def register_contestant_from_form(f):
    c = Contestant()
    c.first_name = f.first_name.data
    c.prefixes = f.prefixes.data
    c.last_name = f.last_name.data
    c.email = f.email.data
    ci = ContestantInfo()
    ci.number = f.number.data
    ci.team = db.session.query(Team).filter_by(city=f.team.data).first()
    ci.contestant = c
    di = DancingInfo()
    if f.ballroom_level.data is None:
        di.not_dancing_ballroom()
    else:
        di.ballroom_level = f.ballroom_level.data
        di.ballroom_role = f.ballroom_role.data
        di.ballroom_blind_date = f.ballroom_blind_date.data
        if f.ballroom_partner.data is None:
            di.ballroom_partner = f.ballroom_partner.data
        else:
            di.ballroom_partner = f.ballroom_partner.data.contestant_info[0].number
            ballroom_partner = db.session.query(Contestant).join(ContestantInfo).filter(ContestantInfo.number == di.ballroom_partner).first()
            ballroom_partner.dancing_info[0].ballroom_partner = ci.number
    if f.latin_level.data is None:
        di.not_dancing_latin()
    else:
        di.latin_level = f.latin_level.data
        di.latin_role = f.latin_role.data
        di.latin_blind_date = f.latin_blind_date.data
        if f.latin_partner.data is None:
            di.latin_partner = f.latin_partner.data
        else:
            di.latin_partner = f.latin_partner.data.contestant_info[0].number
            latin_partner = db.session.query(Contestant).join(ContestantInfo).filter(ContestantInfo.number == di.latin_partner).first()
            latin_partner.dancing_info[0].latin_partner = ci.number
    di.contestant = c
    vi = VolunteerInfo()
    if f.volunteer.data == NO:
        vi.not_volunteering()
    else:
        vi.volunteer = f.volunteer.data
        vi.first_aid = f.first_aid.data
        vi.jury_ballroom = f.jury_ballroom.data
        vi.jury_latin = f.jury_latin.data
    vi.contestant = c
    ai = AdditionalInfo()
    ai.sleeping_arrangements = f.sleeping_arrangement.data
    ai.t_shirt = f.t_shirt.data
    ai.contestant = c
    db.session.add(c)
    db.session.commit()
    return c.get_full_name()


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
    return render_template('dashboard.html', title='Dashboard')


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
        return redirect(url_for('main.add_treasurer'))
    else:
        return render_template('profile.html', form=form)


@bp.route('/add_treasurer', methods=['GET', 'POST'])
@login_required
def add_treasurer():
    form = ChangePasswordForm()
    treasurer_form = TreasurerForm()
    treasurer = db.session.query(User).filter_by(team=current_user.team, access=ACCESS['treasurer']).first()
    if treasurer_form.validate_on_submit():
        tr_pass = random_password()
        treasurer.set_password(tr_pass)
        treasurer.is_active = True
        db.session.commit()
        send_treasurer_activation_email(treasurer_form.email.data, treasurer.username, tr_pass, treasurer_form.message.data)
        flash('Your treasurer now has access to the xTDS WebPortal. Login credentials have been sent to the e-mail provided.', 'alert-info')
        return redirect(url_for('main.profile'))
    return render_template('tc_profile.html', form=form, treasurer_form=treasurer_form, treasurer_active=treasurer.is_active)


@bp.route('/register_dancers', methods=['GET', 'POST'])
@login_required
def register_dancers():
    form = ContestantForm()
    new_id = db.session.query().filter(ContestantInfo.team == current_user.team)\
        .with_entities(db.func.max(ContestantInfo.number)).scalar()
    if new_id is None:
        new_id = 1
    else:
        new_id += 1
    form.number.data = new_id
    form.team.data = current_user.team.city
    form.ballroom_partner.query = Contestant.query.join(ContestantInfo).join(DancingInfo)\
        .filter(ContestantInfo.team == current_user.team,
                DancingInfo.ballroom_partner == None, DancingInfo.ballroom_blind_date == False)
    form.latin_partner.query = Contestant.query.join(ContestantInfo).join(DancingInfo)\
        .filter(ContestantInfo.team == current_user.team,
                DancingInfo.latin_partner == None, DancingInfo.latin_blind_date == False)
    if request.method == 'POST':
        form = contestant_validate_dancing(form)
    if form.validate_on_submit():
        flash('{} has been registered successfully.'.format(register_contestant_from_form(form)), 'alert-success')
        return redirect(url_for('main.register_dancers'))
    return render_template('register_dancers.html', form=form)
