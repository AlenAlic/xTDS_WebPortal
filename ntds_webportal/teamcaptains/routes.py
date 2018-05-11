from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.teamcaptains import bp
from ntds_webportal.teamcaptains.forms import RegisterContestantForm, EditContestantForm, TeamCaptainForm, \
    PartnerRequestForm, PartnerRespondForm, NameChangeRequestForm
from ntds_webportal.models import User, requires_access_level, Team, Contestant, ContestantInfo, DancingInfo, \
    VolunteerInfo, AdditionalInfo, StatusInfo, PartnerRequest, NameChangeRequest

from ntds_webportal.auth.forms import ChangePasswordForm, TreasurerForm
from ntds_webportal.auth.email import random_password, send_treasurer_activation_email
from ntds_webportal.functions import get_dancing_categories, contestant_validate_dancing, submit_contestant
import ntds_webportal.data as data
import itertools
from sqlalchemy import and_, or_


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
    new_id = db.session.query().with_entities(db.func.max(Contestant.contestant_id)).scalar()
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
        .filter(
        ContestantInfo.team == current_user.team,
        DancingInfo.role == data.LEAD) \
        .order_by(DancingInfo.level, ContestantInfo.number).all()
    all_follows = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, DancingInfo.role == data.FOLLOW) \
        .order_by(DancingInfo.level, ContestantInfo.number).all()

    for follow in all_follows:
        for dance in follow.dancing_info:
            if dance.partner is not None:
                c = Contestant.query.filter_by(contestant_id=dance.partner).first()
                if c and not c in all_leads:
                    all_leads.append(c)

    for lead in all_leads:
        for dance in lead.dancing_info:
            if dance.partner is not None:
                c = Contestant.query.filter_by(contestant_id=dance.partner).first()
                if c and not c in all_follows:
                    all_follows.append(c)

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
            partner = next((p.partner for p in request.other.dancing_info if p.competition == request.competition),
                           None)
            if partner is not None:
                success = False
                flash('{} already has a dancing partner'.format(request.other.get_full_name(), partner))

            partner = next((p.partner
                            for p in request.dancer.dancing_info if p.competition == request.competition), None)
            if partner is not None:
                success = False
                flash('{} already has a dancing partner'.format(request.dancer.get_full_name(), partner))

            if success:
                request.accept()
                flash('Dance partner request accepted')
                db.session.commit()
            else:
                return redirect(url_for('teamcaptains.request_respond', request=request.id))
        else:
            request.reject()
            flash('Dance partner request rejected')
        db.session.commit()
        return redirect(url_for('teamcaptains.partner_request_list'))

    return render_template('teamcaptains/request_respond.html', title="Respond to partner request", form=form,
                           req=request)


@bp.route('/name_change_request/<contestant>', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['team_captain']])
def name_change_request(contestant):
    contestant = Contestant.query.filter_by(contestant_id=contestant).first()
    if not contestant:
        return redirect('errors/404.html')
    if not contestant.contestant_info[0].team == current_user.team:
        return redirect('errors/404.html')
    form = NameChangeRequestForm()

    if form.validate_on_submit():
        flash('Name change request send')
        ncr = NameChangeRequest(first_name=form.first_name.data,
                                last_name=form.last_name.data,
                                prefixes=form.prefixes.data,
                                contestant=contestant)
        db.session.add(ncr)
        db.session.commit()
        return redirect(url_for('teamcaptains.edit_dancer', number=contestant.contestant_id))

    form.first_name.data = contestant.first_name
    form.prefixes.data = contestant.prefixes
    form.last_name.data = contestant.last_name

    return render_template('teamcaptains/name_change_request.html', title="Name change request", contestant=contestant,
                           form=form)
