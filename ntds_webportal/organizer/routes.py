from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.organizer import bp
from ntds_webportal.teamcaptains.forms import RegisterContestantForm, EditContestantForm, TeamCaptainForm
from ntds_webportal.models import User, Team, Contestant, ContestantInfo, DancingInfo, VolunteerInfo, AdditionalInfo, \
    StatusInfo
from ntds_webportal.auth.forms import ChangePasswordForm, TreasurerForm
from ntds_webportal.auth.email import random_password, send_treasurer_activation_email
import ntds_webportal.data as data
import itertools
from sqlalchemy import and_, or_

# TODO Registration constraints


def contestant_validate_dancing(form):
    if form.ballroom_partner.data is not None:
        dancing_partner = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo) \
            .filter(ContestantInfo.number == form.ballroom_partner.data.contestant_info[0].number).first()
        if form.ballroom_role.data == dancing_partner.dancing_info[0].ballroom_role:
            if form.ballroom_role.data == data.LEAD:
                form.ballroom_role.data = 'same_role_lead'
            elif form.ballroom_role.data == data.FOLLOW:
                form.ballroom_role.data = 'same_role_follow'
        if form.ballroom_level.data != dancing_partner.dancing_info[0].ballroom_level:
            if dancing_partner.dancing_info[0].ballroom_level is None:
                form.ballroom_level.data = 'diff_levels_no_level'
            elif form.ballroom_level.data != data.CHOOSE:
                form.ballroom_level.data = 'diff_levels'
    if form.latin_partner.data is not None:
        dancing_partner = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo) \
            .filter(ContestantInfo.number == form.latin_partner.data.contestant_info[0].number).first()
        if form.latin_role.data == dancing_partner.dancing_info[0].latin_role:
            if form.latin_role.data == data.LEAD:
                form.latin_role.data = 'same_role_lead'
            elif form.latin_role.data == data.FOLLOW:
                form.latin_role.data = 'same_role_follow'
        if form.latin_level.data != dancing_partner.dancing_info[0].latin_level:
            if dancing_partner.dancing_info[0].latin_level is None:
                form.latin_level.data = 'diff_levels_no_level'
            elif form.latin_level.data != data.CHOOSE:
                form.latin_level.data = 'diff_levels'
    return form


def submit_contestant(f, contestant=None):
    new_dancer = True
    if contestant is None:
        contestant = Contestant()
        ci = ContestantInfo()
        di = DancingInfo()
        vi = VolunteerInfo()
        ai = AdditionalInfo()
        si = StatusInfo()
        contestant.first_name = f.first_name.data
        contestant.prefixes = f.prefixes.data
        contestant.last_name = f.last_name.data
        ci.number = f.number.data
        ci.team = db.session.query(Team).filter_by(name=f.team.data).first()
    else:
        ci = contestant.contestant_info[0]
        di = contestant.dancing_info[0]
        vi = contestant.volunteer_info[0]
        ai = contestant.additional_info[0]
        si = contestant.status_info[0]
        new_dancer = False
    contestant.email = f.email.data
    ci.student = f.student.data
    ci.diet_allergies = f.diet_allergies.data
    ci.contestant = contestant
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
            ballroom_partner = db.session.query(Contestant).join(ContestantInfo)\
                .filter(ContestantInfo.number == di.ballroom_partner).first()
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
            latin_partner = db.session.query(Contestant).join(ContestantInfo)\
                .filter(ContestantInfo.number == di.latin_partner).first()
            latin_partner.dancing_info[0].latin_partner = ci.number
    di.contestant = contestant
    if f.volunteer.data == data.NO:
        vi.not_volunteering()
    else:
        vi.volunteer = f.volunteer.data
        vi.first_aid = f.first_aid.data
        vi.jury_ballroom = f.jury_ballroom.data
        vi.jury_latin = f.jury_latin.data
    vi.contestant = contestant
    ai.sleeping_arrangements = f.sleeping_arrangements.data
    ai.t_shirt = f.t_shirt.data
    ai.contestant = contestant
    si.first_time = f.first_time.data
    si.contestant = contestant
    if new_dancer:
        db.session.add(contestant)
    db.session.commit()
    return contestant.get_full_name()


@bp.route('/add_treasurer', methods=['GET', 'POST'])
@login_required
def add_treasurer():
    form = ChangePasswordForm()
    treasurer_form = TreasurerForm()
    treasurer = db.session.query(User).filter_by(team=current_user.team, access=data.ACCESS['treasurer']).first()
    if treasurer_form.validate_on_submit():
        tr_pass = random_password()
        treasurer.set_password(tr_pass)
        treasurer.is_active = True
        db.session.commit()
        send_treasurer_activation_email(treasurer_form.email.data, treasurer.username, tr_pass,
                                        treasurer_form.message.data)
        flash('Your treasurer now has access to the xTDS WebPortal. '
              'Login credentials have been sent to the e-mail provided.', 'alert-info')
        return redirect(url_for('main.profile'))
    return render_template('teamcaptains/tc_profile.html', form=form, treasurer_form=treasurer_form,
                           treasurer_active=treasurer.is_active)


@bp.route('/register_dancers', methods=['GET', 'POST'])
@login_required
def register_dancers():
    form = RegisterContestantForm()
    new_id = db.session.query().filter(ContestantInfo.team == current_user.team)\
        .with_entities(db.func.max(ContestantInfo.number)).scalar()
    if new_id is None:
        new_id = 1
    else:
        new_id += 1
    form.number.data = new_id
    form.team.data = current_user.team.name
    form.ballroom_partner.query = Contestant.query.join(ContestantInfo).join(DancingInfo)\
        .filter(ContestantInfo.team == current_user.team,
                DancingInfo.ballroom_partner == None, DancingInfo.ballroom_blind_date == False)
    form.latin_partner.query = Contestant.query.join(ContestantInfo).join(DancingInfo)\
        .filter(ContestantInfo.team == current_user.team,
                DancingInfo.latin_partner == None, DancingInfo.latin_blind_date == False)
    if request.method == 'POST':
        form = contestant_validate_dancing(form)
    if form.validate_on_submit():
        flash('{} has been registered successfully.'.format(submit_contestant(form)), 'alert-success')
        return redirect(url_for('teamcaptains.register_dancers'))
    return render_template('teamcaptains/register_dancers.html', form=form)


@bp.route('/registration_overview', methods=['GET', 'POST'])
@login_required
def registration_overview():
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .order_by(ContestantInfo.team_id, ContestantInfo.number).all()
    order = [data.CONFIRMED, data.SELECTED, data.REGISTERED, data.CANCELLED]
    all_dancers = sorted(all_dancers, key=lambda o: (o.contestant_info[0].team_id, order.index(o.status_info[0].status)))
    dancers = [{'country': team['country'], 'name': team['name'], 'id': team['name'].replace(' ','-').replace('`', ''), 'dancers': [dancer for dancer in all_dancers if dancer.contestant_info[0].team.name == team['name']]} for team in data.TEAMS]
    dutch_dancers = [team for team in dancers if team['country'] == data.NETHERLANDS]
    german_dancers = [team for team in dancers if team['country'] == data.GERMANY]
    other_dancers = [team for team in dancers if team['country'] != data.NETHERLANDS and team['country'] != data.GERMANY]
    return render_template('organizer/registration_overview.html', data=data, all_dancers=all_dancers,
                           dutch_dancers=dutch_dancers, german_dancers=german_dancers, other_dancers=other_dancers)


@bp.route('/edit_dancer/<number>', methods=['GET', 'POST'])
@login_required
def edit_dancer(number):
    dancer = db.session.query(Contestant).join(ContestantInfo)\
        .filter(ContestantInfo.team == current_user.team, ContestantInfo.number == number)\
        .order_by(ContestantInfo.number).first_or_404()
    form = EditContestantForm()
    form.full_name.data = dancer.get_full_name()
    form.ballroom_partner.\
        query = Contestant.query.join(ContestantInfo).join(DancingInfo) \
        .filter(and_(ContestantInfo.team == current_user.team,
                     or_(and_(DancingInfo.ballroom_partner == None, DancingInfo.ballroom_blind_date == False),
                         ContestantInfo.number == dancer.dancing_info[0].ballroom_partner)))
    form.latin_partner.query = Contestant.query.join(ContestantInfo).join(DancingInfo) \
        .filter(and_(ContestantInfo.team == current_user.team,
                     or_(and_(DancingInfo.latin_partner == None, DancingInfo.latin_blind_date == False),
                         ContestantInfo.number == dancer.dancing_info[0].latin_partner)))
    if request.method == 'POST':
        form = contestant_validate_dancing(form)
    else:
        form.email.data = dancer.email
        form.student.data = dancer.contestant_info[0].student
        form.diet_allergies.data = dancer.contestant_info[0].diet_allergies
        form.ballroom_level.data = dancer.dancing_info[0].ballroom_level
        form.ballroom_role.data = dancer.dancing_info[0].ballroom_role
        form.ballroom_blind_date.data = dancer.dancing_info[0].ballroom_blind_date
        form.ballroom_partner.data = db.session.query(Contestant).join(ContestantInfo) \
            .filter(ContestantInfo.team == current_user.team,
                    ContestantInfo.number == dancer.dancing_info[0].ballroom_partner).first()
        form.latin_level.data = dancer.dancing_info[0].latin_level
        form.latin_role.data = dancer.dancing_info[0].latin_role
        form.latin_blind_date.data = dancer.dancing_info[0].latin_blind_date
        form.latin_partner.data = db.session.query(Contestant).join(ContestantInfo) \
            .filter(ContestantInfo.team == current_user.team,
                    ContestantInfo.number == dancer.dancing_info[0].latin_partner).first()
        form.volunteer.data = dancer.volunteer_info[0].volunteer
        form.first_aid.data = dancer.volunteer_info[0].first_aid
        form.jury_ballroom.data = dancer.volunteer_info[0].jury_ballroom
        form.jury_latin.data = dancer.volunteer_info[0].jury_latin
        form.sleeping_arrangements.data = dancer.additional_info[0].sleeping_arrangements
        form.t_shirt.data = dancer.additional_info[0].t_shirt
    if form.validate_on_submit():
        flash('{} data has been changed successfully.'.format(submit_contestant(form, contestant=dancer)),
              'alert-success')
        return redirect(url_for('teamcaptains.edit_dancers', wide=int(request.values['wide'])))
    return render_template('teamcaptains/edit_dancer.html', dancer=dancer, form=form, data=data)


@bp.route('/register_dancer/<number>', methods=['GET', 'POST'])
@login_required
def register_dancer(number):
    register = request.args.get('register', None, type=int)
    changed_dancer = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, ContestantInfo.number == number).first()
    if register == 0:
        changed_dancer.status_info[0].status = data.CANCELLED
        db.session.commit()
        flash('The registration of {} has been cancelled.'.format(changed_dancer.get_full_name()), 'alert-info')
    elif register == 1:
        changed_dancer.status_info[0].status = data.REGISTERED
        db.session.commit()
        flash('{} has been re-registered successfully.'.format(changed_dancer.get_full_name()), 'alert-success')
    return redirect(url_for('teamcaptains.edit_dancers', wide=int(request.values['wide'])))

@bp.route('/set_teamcaptains', methods=['GET', 'POST'])
@login_required
def set_teamcaptains():
    form = TeamCaptainForm()
    form.number.query = Contestant.query.join(ContestantInfo).filter(ContestantInfo.team == current_user.team)
    current_tc = db.session.query(Contestant).join(ContestantInfo)\
        .filter(ContestantInfo.team == current_user.team, ContestantInfo.team_captain == True).first()
    if form.validate_on_submit():
        if form.number.data is not None:
            new_tc = db.session.query(Contestant)\
                .filter(Contestant.contestant_id == form.number.data.contestant_id).first()
            new_tc.contestant_info[0].set_teamcaptain()
            flash('Set {} as team captain.'.format(new_tc.get_full_name()), 'alert-success')
            return redirect(url_for('teamcaptains.set_teamcaptains'))
        else:
            current_tc.contestant_info[0].team_captain = False
            db.session.commit()
            flash('Removed {} as team captain.'.format(current_tc.get_full_name()))
            return redirect(url_for('teamcaptains.set_teamcaptains'))
    return render_template('teamcaptains/set_teamcaptains.html', form=form, current_tc=current_tc)


@bp.route('/couples_list', methods=['GET', 'POST'])
@login_required
def couples_list():
    confirmed = request.args.get('confirmed', 0, type=int)
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo)\
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == data.CONFIRMED)\
        .order_by(DancingInfo.ballroom_level, ContestantInfo.number).all()
    ballroom_couples_leads = [dancer for dancer in all_dancers if dancer.dancing_info[0].ballroom_role == data.LEAD and
                              dancer.dancing_info[0].ballroom_partner is not None]
    ballroom_couples_follows = [dancer for dancer in all_dancers if dancer.dancing_info[0].ballroom_partner in 
                                [lead.contestant_info[0].number for lead in ballroom_couples_leads]]
    latin_couples_leads = [dancer for dancer in all_dancers if dancer.dancing_info[0].latin_role == data.LEAD and
                              dancer.dancing_info[0].latin_partner is not None]
    latin_couples_follows = [dancer for dancer in all_dancers if dancer.dancing_info[0].latin_partner in
                                [lead.contestant_info[0].number for lead in latin_couples_leads]]
    ballroom_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                        list(itertools.product(ballroom_couples_leads, ballroom_couples_follows)) if
                        couple[0].contestant_info[0].number == couple[1].dancing_info[0].ballroom_partner]
    latin_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                     list(itertools.product(latin_couples_leads, latin_couples_follows)) if
                     couple[0].contestant_info[0].number == couple[1].dancing_info[0].latin_partner]
    ballroom_lead_blind_daters = [dancer for dancer in all_dancers if
                                  dancer.dancing_info[0].ballroom_role == data.LEAD and
                                  dancer.dancing_info[0].ballroom_partner is None]
    ballroom_follow_blind_daters = [dancer for dancer in all_dancers if
                                    dancer.dancing_info[0].ballroom_role == data.FOLLOW and
                                    dancer.dancing_info[0].ballroom_partner is None]
    latin_lead_blind_daters = [dancer for dancer in all_dancers if
                               dancer.dancing_info[0].latin_role == data.LEAD and
                               dancer.dancing_info[0].latin_partner is None]
    latin_follow_blind_daters = [dancer for dancer in all_dancers if
                                 dancer.dancing_info[0].latin_role == data.FOLLOW and
                                 dancer.dancing_info[0].latin_partner is None]
    return render_template('teamcaptains/couples_lists.html', data=data, confirmed=confirmed,
                           ballroom_couples=ballroom_couples, latin_couples=latin_couples,
                           ballroom_lead_blind_daters=ballroom_lead_blind_daters,
                           ballroom_follow_blind_daters=ballroom_follow_blind_daters,
                           latin_lead_blind_daters=latin_lead_blind_daters,
                           latin_follow_blind_daters=latin_follow_blind_daters)


@bp.route('/edit_finances', methods=['GET', 'POST'])
@login_required
def edit_finances():
    # TODO Stan zeurt, wil het graag exporteerbaar naar CSV (naam, bedrag, omschrijving)
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .filter(ContestantInfo.team == current_user.team, StatusInfo.payment_required == True)\
        .order_by(ContestantInfo.number).all()
    confirmed_dancers = [d for d in all_dancers if d.status_info[0].status == data.CONFIRMED]
    cancelled_dancers = [d for d in all_dancers if d.status_info[0].status == data.CANCELLED]
    finances = data.finances_overview(all_dancers)
    if request.method == 'POST':
        changes = False
        for dancer in all_dancers:
            if request.form.get(str(dancer.contestant_info[0].number)) is not None:
                if not dancer.status_info[0].paid:
                    changes = True
                dancer.status_info[0].paid = True
            else:
                if dancer.status_info[0].paid:
                    changes = True
                dancer.status_info[0].paid = False
        if changes:
            db.session.commit()
            flash('Changes saved successfully.', 'alert-success')
        else:
            flash('No changes were made to submit.', 'alert-warning')
    return render_template('teamcaptains/edit_finances.html', finances=finances, confirmed_dancers=confirmed_dancers,
                           cancelled_dancers=cancelled_dancers, data=data)
