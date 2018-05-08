from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.teamcaptains import bp
from ntds_webportal.teamcaptains.forms import RegisterContestantForm, EditContestantForm, TeamCaptainForm, \
    PartnerRequestForm, PartnerRespondForm
from ntds_webportal.models import User, requires_access_level, Team, Contestant, ContestantInfo, DancingInfo, \
    VolunteerInfo, AdditionalInfo, StatusInfo, PartnerRequest
from ntds_webportal.auth.forms import ChangePasswordForm, TreasurerForm
from ntds_webportal.auth.email import random_password, send_treasurer_activation_email
import ntds_webportal.data as data
import itertools
from sqlalchemy import and_, or_


def contestant_validate_dancing(form):
    if form.ballroom_partner.data is not None:
        if form.ballroom_level.data in data.BLIND_DATE_LEVELS:
            form.ballroom_partner.data = 'must_blind_date'
        else:
            # noinspection PyUnresolvedReferences
            dancing_partner = db.session.query(Contestant) \
                .filter(Contestant.contestant_id == form.ballroom_partner.data.contestant_id).first()
            dancing_categories = get_dancing_categories(dancing_partner.dancing_info)
            if form.ballroom_level.data != dancing_categories[data.BALLROOM].level:
                if dancing_categories[data.BALLROOM].level is None:
                    form.ballroom_partner.data = 'diff_levels_no_level'
                    form.ballroom_level.data = 'diff_levels_no_level'
                elif form.ballroom_level.data != data.CHOOSE:
                    form.ballroom_partner.data = 'diff_levels'
                    form.ballroom_level.data = 'diff_levels'
            if form.ballroom_role.data == dancing_categories[data.BALLROOM].role:
                if form.ballroom_role.data == data.LEAD:
                    form.ballroom_partner.data = 'same_role_lead'
                    form.ballroom_role.data = 'same_role_lead'
                elif form.ballroom_role.data == data.FOLLOW:
                    form.ballroom_partner.data = 'same_role_follow'
                    form.ballroom_role.data = 'same_role_follow'
    if form.latin_partner.data is not None:
        if form.latin_level.data in data.BLIND_DATE_LEVELS:
            form.latin_partner.data = 'must_blind_date'
        else:
            # noinspection PyUnresolvedReferences
            dancing_partner = db.session.query(Contestant) \
                .filter(Contestant.contestant_id == form.latin_partner.data.contestant_id).first()
            dancing_categories = get_dancing_categories(dancing_partner.dancing_info)
            if form.latin_level.data != dancing_categories[data.LATIN].level:
                if dancing_categories[data.LATIN].level is None:
                    form.latin_partner.data = 'diff_levels_no_level'
                    form.latin_level.data = 'diff_levels_no_level'
                elif form.latin_level.data != data.CHOOSE:
                    form.latin_partner.data = 'diff_levels'
                    form.latin_level.data = 'diff_levels'
            if form.latin_role.data == dancing_categories[data.LATIN].role:
                if form.latin_role.data == data.LEAD:
                    form.latin_partner.data = 'same_role_lead'
                    form.latin_role.data = 'same_role_lead'
                elif form.latin_role.data == data.FOLLOW:
                    form.latin_partner.data = 'same_role_follow'
                    form.latin_role.data = 'same_role_follow'
    return form


def submit_contestant(f, contestant=None):
    new_dancer = True
    if contestant is None:
        contestant = Contestant()
        ci = ContestantInfo()
        di = DancingInfo()
        dancing_categories = {cat: DancingInfo(competition=cat) for cat in data.ALL_CATEGORIES}
        vi = VolunteerInfo()
        ai = AdditionalInfo()
        si = StatusInfo()
        contestant.first_name = f.first_name.data
        contestant.prefixes = f.prefixes.data if f.prefixes.data is not '' else None
        contestant.last_name = f.last_name.data
        ci.number = f.number.data
        ci.team = db.session.query(Team).filter_by(name=f.team.data).first()
    else:
        ci = contestant.contestant_info[0]
        di = contestant.dancing_info
        vi = contestant.volunteer_info[0]
        ai = contestant.additional_info[0]
        si = contestant.status_info[0]
        dancing_categories = get_dancing_categories(di)
        new_dancer = False
    contestant.email = f.email.data
    ci.contestant = contestant
    ci.student = f.student.data
    ci.diet_allergies = f.diet_allergies.data
    dancing_categories[data.BALLROOM].contestant = contestant
    dancing_categories[data.LATIN].contestant = contestant
    if f.ballroom_level.data is None:
        dancing_categories[data.BALLROOM].not_dancing(data.BALLROOM)
    else:
        dancing_categories[data.BALLROOM].level = f.ballroom_level.data
        dancing_categories[data.BALLROOM].role = f.ballroom_role.data
        dancing_categories[data.BALLROOM].blind_date = f.ballroom_blind_date.data
        db.session.add(dancing_categories[data.BALLROOM])
        db.session.flush()
        if f.ballroom_partner.data is not None:
            dancing_categories[data.BALLROOM].set_partner(f.ballroom_partner.data.contestant_id)
        else:
            dancing_categories[data.BALLROOM].set_partner(None)
    if f.latin_level.data is None:
        dancing_categories[data.LATIN].not_dancing(data.LATIN)
    else:
        dancing_categories[data.LATIN].level = f.latin_level.data
        dancing_categories[data.LATIN].role = f.latin_role.data
        dancing_categories[data.LATIN].blind_date = f.latin_blind_date.data
        db.session.add(dancing_categories[data.LATIN])
        db.session.flush()
        if f.latin_partner.data is not None:
            dancing_categories[data.LATIN].set_partner(f.latin_partner.data.contestant_id)
        else:
            dancing_categories[data.LATIN].set_partner(None)
    vi.contestant = contestant
    if f.volunteer.data == data.NO:
        vi.not_volunteering()
    else:
        vi.volunteer = f.volunteer.data
        vi.first_aid = f.first_aid.data
        vi.jury_ballroom = f.jury_ballroom.data
        vi.jury_latin = f.jury_latin.data
    ai.contestant = contestant
    ai.sleeping_arrangements = f.sleeping_arrangements.data
    ai.t_shirt = f.t_shirt.data
    si.contestant = contestant
    si.first_time = f.first_time.data
    if new_dancer:
        db.session.add(contestant)
    db.session.commit()
    return contestant.get_full_name()


def get_dancing_categories(dancing_info):
    return {di.competition: di for di in dancing_info}


@bp.route('/add_treasurer', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['team_captain']])
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
@requires_access_level([data.ACCESS['team_captain']])
def register_dancers():
    form = RegisterContestantForm()
    new_id = db.session.query().filter(ContestantInfo.team == current_user.team) \
        .with_entities(db.func.max(ContestantInfo.number)).scalar()
    if new_id is None:
        new_id = 1
    else:
        new_id += 1
    form.number.data = new_id
    form.team.data = current_user.team.name
    form.ballroom_partner.query = Contestant.query.join(ContestantInfo).join(DancingInfo) \
        .filter(ContestantInfo.team == current_user.team, DancingInfo.competition == data.BALLROOM,
                DancingInfo.blind_date.is_(False), DancingInfo.partner.is_(None))
    form.latin_partner.query = Contestant.query.join(ContestantInfo).join(DancingInfo) \
        .filter(ContestantInfo.team == current_user.team, DancingInfo.competition == data.LATIN,
                DancingInfo.blind_date.is_(False), DancingInfo.partner.is_(None))
    if request.method == 'POST':
        # noinspection PyTypeChecker
        form = contestant_validate_dancing(form)
    if form.validate_on_submit():
        flash('{} has been registered successfully.'.format(submit_contestant(form)), 'alert-success')
        return redirect(url_for('teamcaptains.register_dancers'))
    return render_template('teamcaptains/register_dancers.html', form=form)


@bp.route('/edit_dancers', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['team_captain']])
def edit_dancers():
    wide = request.args.get('wide', 0, type=int)
    dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team).order_by(ContestantInfo.number).all()
    order = [data.CONFIRMED, data.SELECTED, data.REGISTERED, data.CANCELLED]
    dancers = sorted(dancers, key=lambda o: order.index(o.status_info[0].status))
    return render_template('teamcaptains/edit_dancers.html', dancers=dancers, data=data, wide=wide)


@bp.route('/edit_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['team_captain']])
def edit_dancer(number):
    dancer = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, Contestant.contestant_id == number) \
        .order_by(Contestant.contestant_id).first_or_404()
    form = EditContestantForm()
    form.full_name.data = dancer.get_full_name()
    form.team.data = dancer.contestant_info[0].team.name
    form.number.data = dancer.contestant_info[0].number
    form.ballroom_partner.query = Contestant.query.join(ContestantInfo).join(DancingInfo) \
        .filter(and_(ContestantInfo.team == current_user.team, DancingInfo.competition == data.BALLROOM,
                     Contestant.contestant_id != dancer.contestant_id,
                     or_(and_(DancingInfo.blind_date.is_(False), DancingInfo.partner.is_(None),
                              DancingInfo.level != data.NO), and_(DancingInfo.competition == data.BALLROOM,
                                                                  DancingInfo.partner == dancer.contestant_id))))
    form.latin_partner.query = Contestant.query.join(ContestantInfo).join(DancingInfo) \
        .filter(and_(ContestantInfo.team == current_user.team, DancingInfo.competition == data.LATIN,
                     Contestant.contestant_id != dancer.contestant_id,
                     or_(and_(DancingInfo.blind_date.is_(False), DancingInfo.partner.is_(None),
                              DancingInfo.level != data.NO), and_(DancingInfo.competition == data.LATIN,
                                                                  DancingInfo.partner == dancer.contestant_id))))
    if request.method == 'POST':
        # noinspection PyTypeChecker
        form = contestant_validate_dancing(form)
    else:
        form.email.data = dancer.email
        form.student.data = dancer.contestant_info[0].student
        form.diet_allergies.data = dancer.contestant_info[0].diet_allergies
        dancing_categories = get_dancing_categories(dancer.dancing_info)
        form.ballroom_level.data = dancing_categories[data.BALLROOM].level
        form.ballroom_role.data = dancing_categories[data.BALLROOM].role
        form.ballroom_blind_date.data = dancing_categories[data.BALLROOM].blind_date
        form.ballroom_partner.data = db.session.query(Contestant).join(ContestantInfo) \
            .filter(ContestantInfo.team == current_user.team,
                    Contestant.contestant_id == dancing_categories[data.BALLROOM].partner).first()
        form.latin_level.data = dancing_categories[data.LATIN].level
        form.latin_role.data = dancing_categories[data.LATIN].role
        form.latin_blind_date.data = dancing_categories[data.LATIN].blind_date
        form.latin_partner.data = db.session.query(Contestant).join(ContestantInfo) \
            .filter(ContestantInfo.team == current_user.team,
                    Contestant.contestant_id == dancing_categories[data.LATIN].partner).first()
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
@requires_access_level([data.ACCESS['team_captain']])
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
@requires_access_level([data.ACCESS['team_captain']])
def set_teamcaptains():
    form = TeamCaptainForm()
    form.number.query = Contestant.query.join(ContestantInfo).filter(ContestantInfo.team == current_user.team)
    current_tc = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, ContestantInfo.team_captain.is_(True)).first()
    if form.validate_on_submit():
        if form.number.data is not None:
            new_tc = db.session.query(Contestant) \
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


@bp.route('/couples_list')
@login_required
@requires_access_level([data.ACCESS['team_captain']])
def couples_list():
    confirmed = request.args.get('confirmed', 0, type=int)
    all_leads = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, DancingInfo.role == data.LEAD) \
        .order_by(DancingInfo.level, ContestantInfo.number).all()
    all_follows = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, DancingInfo.role == data.FOLLOW) \
        .order_by(DancingInfo.level, ContestantInfo.number).all()
    ballroom_couples_leads = [dancer for dancer in all_leads if
                              get_dancing_categories(dancer.dancing_info)[data.BALLROOM].role == data.LEAD and
                              get_dancing_categories(dancer.dancing_info)[data.BALLROOM].partner is not None]
    ballroom_couples_follows = [dancer for dancer in all_follows if
                                get_dancing_categories(dancer.dancing_info)[data.BALLROOM].role == data.FOLLOW and
                                get_dancing_categories(dancer.dancing_info)[data.BALLROOM].partner is not None]
    latin_couples_leads = [dancer for dancer in all_leads if
                           get_dancing_categories(dancer.dancing_info)[data.LATIN].role == data.LEAD and
                           get_dancing_categories(dancer.dancing_info)[data.LATIN].partner is not None]
    latin_couples_follows = [dancer for dancer in all_follows if
                             get_dancing_categories(dancer.dancing_info)[data.LATIN].role == data.FOLLOW and
                             get_dancing_categories(dancer.dancing_info)[data.LATIN].partner is not None]
    ballroom_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                        list(itertools.product(ballroom_couples_leads, ballroom_couples_follows)) if
                        couple[0].contestant_id == get_dancing_categories(
                            couple[1].dancing_info)[data.BALLROOM].partner]
    latin_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                     list(itertools.product(latin_couples_leads, latin_couples_follows)) if
                     couple[0].contestant_id == get_dancing_categories(couple[1].dancing_info)[data.LATIN].partner]
    confirmed_ballroom_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                                  list(itertools.product([dancer for dancer in ballroom_couples_leads if
                                                          dancer.status_info[0].status == data.CONFIRMED],
                                                         [dancer for dancer in ballroom_couples_follows if
                                                          dancer.status_info[0].status == data.CONFIRMED])) if
                                  couple[0].contestant_id == get_dancing_categories(
                                      couple[1].dancing_info)[data.BALLROOM].partner]
    confirmed_latin_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                               list(itertools.product([dancer for dancer in latin_couples_leads
                                                       if dancer.status_info[0].status == data.CONFIRMED],
                                                      [dancer for dancer in latin_couples_follows
                                                       if dancer.status_info[0].status == data.CONFIRMED])) if
                               couple[0].contestant_id == get_dancing_categories(
                                   couple[1].dancing_info)[data.LATIN].partner]
    ballroom_lead_blind_daters = [dancer for dancer in all_leads if
                                  get_dancing_categories(dancer.dancing_info)[data.BALLROOM].role == data.LEAD and
                                  get_dancing_categories(dancer.dancing_info)[data.BALLROOM].partner is None and
                                  dancer.status_info[0].status == data.CONFIRMED]
    ballroom_follow_blind_daters = [dancer for dancer in all_follows if
                                    get_dancing_categories(dancer.dancing_info)[data.BALLROOM].role == data.FOLLOW and
                                    get_dancing_categories(dancer.dancing_info)[data.BALLROOM].partner is None and
                                    dancer.status_info[0].status == data.CONFIRMED]
    latin_lead_blind_daters = [dancer for dancer in all_leads if
                               get_dancing_categories(dancer.dancing_info)[data.LATIN].role == data.LEAD and
                               get_dancing_categories(dancer.dancing_info)[data.LATIN].partner is None and
                               dancer.status_info[0].status == data.CONFIRMED]
    latin_follow_blind_daters = [dancer for dancer in all_follows if
                                 get_dancing_categories(dancer.dancing_info)[data.LATIN].role == data.FOLLOW and
                                 get_dancing_categories(dancer.dancing_info)[data.LATIN].partner is None and
                                 dancer.status_info[0].status == data.CONFIRMED]
    return render_template('teamcaptains/couples_lists.html', data=data, confirmed=confirmed,
                           ballroom_couples=ballroom_couples, latin_couples=latin_couples,
                           confirmed_ballroom_couples=confirmed_ballroom_couples,
                           confirmed_latin_couples=confirmed_latin_couples,
                           ballroom_lead_blind_daters=ballroom_lead_blind_daters,
                           ballroom_follow_blind_daters=ballroom_follow_blind_daters,
                           latin_lead_blind_daters=latin_lead_blind_daters,
                           latin_follow_blind_daters=latin_follow_blind_daters)


@bp.route('/edit_finances', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['team_captain'], data.ACCESS['treasurer']])
def edit_finances():
    # TODO Stan zeurt, wil het graag exporteerbaar naar CSV (naam, bedrag, omschrijving), lage prio
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, StatusInfo.payment_required.is_(True)) \
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
        return redirect(url_for('teamcaptains.edit_finances'))
    return render_template('teamcaptains/edit_finances.html', finances=finances,
                           confirmed_dancers=confirmed_dancers, cancelled_dancers=cancelled_dancers, data=data)


@bp.route('/partner_request', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['team_captain']])
def partner_request():
    form = PartnerRequestForm()
    form.dancer.choices = map(lambda c: (c.contestant_id, c.contestant.get_full_name()),
                              ContestantInfo.query.filter_by(team=current_user.team).join(
                                  ContestantInfo.contestant).join(Contestant.dancing_info).all())
    form.other.choices = map(lambda c: (c.contestant_id, "{} - {}".format(c.contestant.get_full_name(), c.team)),
                             ContestantInfo.query.filter(ContestantInfo.team != current_user.team).join(
                                 ContestantInfo.contestant).join(Contestant.dancing_info).all())

    if form.validate_on_submit():
        di1 = DancingInfo.query.filter_by(contestant_id=form.dancer.data, competition=form.competition.data).first()
        di2 = DancingInfo.query.filter_by(contestant_id=form.other.data, competition=form.competition.data).first()
        match, errors = di1.valid_match(di2)
        if not match:
            flash("The dancers {} and {} are not a valid couple because:".format(di1.contestant, di2.contestant),
                  'alert-danger')
            for e in errors:
                flash(e, 'alert-danger')
            return redirect(url_for('teamcaptains.partner_request'))
        else:
            pr = PartnerRequest(dancer_id=form.dancer.data, other_id=form.other.data, remark=form.remark.data,
                                competition=form.competition.data, level=form.level.data)
            print(pr)
            db.session.add(pr)
            db.session.commit()
            flash('Partner request created, please wait untill the other teamcaptain had accepted the request')
            return redirect(url_for('teamcaptains.partner_request'))

    return render_template('teamcaptains/partner_request.html', form=form, title='partner_request')


@bp.route('/partner_request_list', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['team_captain']])
def partner_request_list():
    requests = PartnerRequest.query.all()
    myrequests = list(request for request in requests if request.dancer.contestant_info[0].team == current_user.team)
    otherrequests = list(request for request in requests if
                     request.other.contestant_info[0].team == current_user.team and request.state ==
                     PartnerRequest.STATE['Open'])
    return render_template('teamcaptains/partner_list.html', myrequests=myrequests, otherrequests=otherrequests,
                           title='partner requests')


@bp.route('/partner_request/<request>/', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['team_captain']])
def request_respond(request):
    request = PartnerRequest.query.filter_by(id=request).first()
    if not request:
        return redirect('errors/404.html')
    if request.other.contestant_info[0].team != current_user.team:
        return redirect('errors/404.html')

    form = PartnerRespondForm()
    if form.validate_on_submit():
        accepted = form.accept.data
        request.response = form.remark.data
        if accepted:
            success = True
            partner = next((p.partner for p in request.other.dancing_info if p.competition==request.competition),None)
            if partner is not None:
                success = False
                flash('{} already has a dancing partner'.format(request.other.get_full_name(), partner))

            partner = next((p.partner
            for p in request.dancer.dancing_info if p.competition == request.competition),None)
            if partner is not None:
                success=False
                flash('{} already has a dancing partner'.format(request.dancer.get_full_name(), partner))

            if success:
                request.accept()
                flash('Dance partner request accepted')
                db.session.commit()
            else:
                return redirect(url_for('teamcaptains.request_respond',request=request.id))
        else:
            request.reject()
            flash('Dance partner request rejected')
        db.session.commit()
        return redirect(url_for('teamcaptains.partner_request_list'))

    return render_template('teamcaptains/request_respond.html', title="Respond to partner request", form=form,
                           req=request)
