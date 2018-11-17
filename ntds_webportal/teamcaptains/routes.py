from flask import render_template, url_for, redirect, flash, request, send_file
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.teamcaptains import bp
from ntds_webportal.teamcaptains.forms import RegisterContestantForm, EditContestantForm, TeamCaptainForm, \
    PartnerRequestForm, PartnerRespondForm, NameChangeRequestForm, CreateCoupleForm
from ntds_webportal.models import User, requires_access_level, TeamFinances, Contestant, ContestantInfo, DancingInfo, \
    StatusInfo, PartnerRequest, NameChangeRequest, TournamentState, Notification, Merchandise, AdditionalInfo, Team
from ntds_webportal.auth.forms import ChangePasswordForm, TreasurerForm
from ntds_webportal.auth.email import random_password, send_treasurer_activation_email
from ntds_webportal.functions import get_dancing_categories, contestant_validate_dancing, submit_contestant, \
    get_total_dancer_price_list, populate_registration_form
import ntds_webportal.functions as func
import ntds_webportal.data as data
from ntds_webportal.data import *
from sqlalchemy import and_, or_
import itertools
import datetime
import xlsxwriter
from io import BytesIO, StringIO
import csv


@bp.route('/teamcaptain_profile', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def teamcaptain_profile():
    form = ChangePasswordForm()
    treasurer_form = TreasurerForm()
    treasurer = db.session.query(User).filter_by(team=current_user.team, access=ACCESS['treasurer']).first()
    if treasurer_form.validate_on_submit():
        tr_pass = random_password()
        treasurer.set_password(tr_pass)
        treasurer.email = treasurer_form.email.data
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
@requires_access_level([ACCESS['team_captain']])
def register_dancers():
    form = RegisterContestantForm()
    if request.method == POST:
        form.custom_validate()
    if form.validate_on_submit():
        if 'privacy_checkbox' in request.values:
            flash('{} has been registered successfully.'.format(submit_contestant(form)), 'alert-success')
            return redirect(url_for('teamcaptains.register_dancers'))
        else:
            flash('You can not register without accepting the privacy statement.', 'alert-danger')
    else:
        if form.is_submitted():
            flash('Not all fields of the form have been filled in (correctly).', 'alert-danger')
    possible_partners = TeamPossiblePartners(current_user, include_gdpr=True).possible_partners()
    return render_template('teamcaptains/register_dancers.html', form=form, data=data,
                           timestamp=datetime.datetime.now().timestamp(), merchandise=merchandise)


@bp.route('/edit_dancers', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def edit_dancers():
    wide = request.args.get('wide', 0, type=int)
    dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team).order_by(ContestantInfo.number).all()
    order = [CONFIRMED, SELECTED, REGISTERED, CANCELLED]
    dancers = sorted(dancers, key=lambda o: order.index(o.status_info[0].status))
    return render_template('teamcaptains/edit_dancers.html', dancers=dancers, data=data, wide=wide)


@bp.route('/edit_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def edit_dancer(number):
    wide = int(request.values['wide'])
    dancer = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, Contestant.contestant_id == number) \
        .order_by(Contestant.contestant_id).first_or_404()
    possible_partners = TeamPossiblePartners(current_user, include_external_partners_of=dancer).possible_partners()
    form = EditContestantForm(dancer)
    if request.method == GET:
        form.populate(dancer)
    if request.method == POST:
        form.custom_validate(dancer)
    if form.validate_on_submit():
        flash('{} data has been changed successfully.'.format(submit_contestant(form, contestant=dancer)),
              'alert-success')
        return redirect(url_for('teamcaptains.edit_dancers', wide=wide))
    return render_template('teamcaptains/edit_dancer.html', dancer=dancer, form=form, data=data, state=state, wide=wide,
                           timestamp=datetime.datetime.now().timestamp())


@bp.route('/register_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def register_dancer(number):
    register = request.args.get('register', None, type=int)
    send_message = request.args.get('send_message', False, type=bool)
    changed_dancer = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, Contestant.contestant_id == number).first()
    if register == 0:
        status = changed_dancer.status_info[0].status
        changed_dancer.cancel_registration()
        db.session.commit()
        flash('The registration of {} has been cancelled.'.format(changed_dancer.get_full_name()), 'alert-info')
        if send_message:
            text = f"{changed_dancer.get_full_name()} from team {changed_dancer.contestant_info[0].team.name} " \
                   f"has cancelled his/her registration.\n"
            n = Notification(title=f"Cancelled registration, previously {status}", text=text,
                             user=User.query.filter(User.access == ACCESS['organizer']).first())
            db.session.add(n)
            db.session.commit()
    elif register == 1:
        changed_dancer.status_info[0].set_status(REGISTERED)
        db.session.commit()
        flash('{} has been re-registered successfully.'.format(changed_dancer.get_full_name()), 'alert-success')
    return redirect(url_for('teamcaptains.edit_dancers', wide=int(request.values['wide'])))


@bp.route('/name_change_request/<contestant>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def name_change_request(contestant):
    wide = int(request.values['wide'])
    contestant = Contestant.query.filter_by(contestant_id=contestant).first()
    if not contestant or not contestant.contestant_info[0].team == current_user.team:
        return redirect('errors/404.html')
    form = NameChangeRequestForm()
    if form.validate_on_submit():
        flash('Name change request sent.')
        ncr = NameChangeRequest(first_name=form.first_name.data, last_name=form.last_name.data,
                                prefixes=form.prefixes.data, contestant=contestant)
        db.session.add(ncr)
        db.session.commit()
        return redirect(url_for('teamcaptains.edit_dancer', number=contestant.contestant_id, wide=wide))
    form.first_name.data = contestant.first_name
    form.prefixes.data = contestant.prefixes
    form.last_name.data = contestant.last_name
    return render_template('teamcaptains/name_change_request.html', title="Name change request", contestant=contestant,
                           form=form, wide=wide)


@bp.route('/couples_list', methods=['GET'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def couples_list():
    all_leads = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, DancingInfo.role == LEAD) \
        .order_by(DancingInfo.level, Contestant.first_name).all()
    all_follows = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, DancingInfo.role == FOLLOW) \
        .order_by(DancingInfo.level, ContestantInfo.number).all()

    for follow in all_follows:
        for dance in follow.dancing_info:
            if dance.partner is not None:
                c = Contestant.query.filter_by(contestant_id=dance.partner).first()
                if c and c not in all_leads:
                    all_leads.append(c)

    for lead in all_leads:
        for dance in lead.dancing_info:
            if dance.partner is not None:
                c = Contestant.query.filter_by(contestant_id=dance.partner).first()
                if c and c not in all_follows:
                    all_follows.append(c)

    ballroom_couples_leads = [dancer for dancer in all_leads if
                              get_dancing_categories(dancer.dancing_info)[BALLROOM].role == LEAD and
                              get_dancing_categories(dancer.dancing_info)[BALLROOM].partner is not None]
    ballroom_couples_follows = [dancer for dancer in all_follows if
                                get_dancing_categories(dancer.dancing_info)[BALLROOM].role == FOLLOW and
                                get_dancing_categories(dancer.dancing_info)[BALLROOM].partner is not None]
    latin_couples_leads = [dancer for dancer in all_leads if
                           get_dancing_categories(dancer.dancing_info)[LATIN].role == LEAD and
                           get_dancing_categories(dancer.dancing_info)[LATIN].partner is not None]
    latin_couples_follows = [dancer for dancer in all_follows if
                             get_dancing_categories(dancer.dancing_info)[LATIN].role == FOLLOW and
                             get_dancing_categories(dancer.dancing_info)[LATIN].partner is not None]
    ballroom_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                        list(itertools.product(ballroom_couples_leads, ballroom_couples_follows)) if
                        couple[0].contestant_id == get_dancing_categories(couple[1].dancing_info)[BALLROOM].partner]
    ballroom_couples = [couple for couple in ballroom_couples if
                        couple['lead'].contestant_info[0].team == current_user.team
                        or couple['follow'].contestant_info[0].team == current_user.team]
    latin_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                     list(itertools.product(latin_couples_leads, latin_couples_follows)) if
                     couple[0].contestant_id == get_dancing_categories(couple[1].dancing_info)[LATIN].partner]
    latin_couples = [couple for couple in latin_couples if couple['lead'].contestant_info[0].team == current_user.team
                     or couple['follow'].contestant_info[0].team == current_user.team]
    return render_template('teamcaptains/couples_lists.html', data=data, func=func,
                           ballroom_couples=ballroom_couples, latin_couples=latin_couples)


@bp.route('/create_couple', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def create_couple():
    form = CreateCoupleForm()
    leads = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo)\
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == REGISTERED,
                DancingInfo.role == LEAD, DancingInfo.partner.is_(None),
                or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                    DancingInfo.level == BEGINNERS)).order_by(Contestant.first_name)
    follows = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == REGISTERED,
                DancingInfo.role == FOLLOW, DancingInfo.partner.is_(None),
                or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                    DancingInfo.level == BEGINNERS)).order_by(Contestant.first_name)
    if len(leads.all()) == 0 or len(follows.all()) == 0:
        flash(f"There are currently {len(leads.all())} available Leads and {len(follows.all())} available Follows "
              f"registered. Cannot create new couples.", 'alert-warning')
        return redirect(url_for('teamcaptains.couples_list'))
    form.lead.query = leads
    form.follow.query = follows
    if form.validate_on_submit():
        lead = DancingInfo.query.filter_by(contestant_id=form.lead.data.contestant_id,
                                           competition=form.competition.data).first()
        follow = DancingInfo.query.filter_by(contestant_id=form.follow.data.contestant_id,
                                             competition=form.competition.data).first()
        match, errors = lead.valid_match(follow)
        if not match:
            flash("{} and {} are not a valid couple:"
                  .format(lead.contestant.get_full_name(), follow.contestant.get_full_name()), 'alert-danger')
            for e in errors:
                flash(e, 'alert-warning')
        else:
            lead.set_partner(follow.contestant_id)
            db.session.commit()
            flash(f'Created a couple with {lead.contestant} and {follow.contestant} in {form.competition.data}.',
                  'alert-success')
            return redirect(url_for('teamcaptains.couples_list'))
    return render_template('teamcaptains/create_couple.html', form=form)


@bp.route('/break_up_couple/<competition>,<lead_id>,<follow_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def break_up_couple(competition, lead_id, follow_id):
    lead = DancingInfo.query.filter(DancingInfo.competition == competition, DancingInfo.contestant_id == lead_id,
                                    DancingInfo.partner == follow_id).first()
    follow = Contestant.query.filter(Contestant.contestant_id == follow_id).first()
    lead_status = Contestant.query.filter(Contestant.contestant_id == lead_id).first()
    if lead_status.status_info[0].status == SELECTED or lead_status.status_info[0].status == CONFIRMED \
            or follow.status_info[0].status == SELECTED or follow.status_info[0].status == CONFIRMED:
        flash(f"Cannot break up a couple that has been {SELECTED} or {CONFIRMED}.")
    else:
        lead.set_partner(None)
        db.session.commit()
        flash(f'{lead.contestant} and {follow} are not a couple anymore in {competition}.')
        dancer = None
        if lead_status.contestant_info[0].team != current_user.team:
            dancer, old_partner = lead_status, follow
        elif follow.contestant_info[0].team != current_user.team:
            dancer, old_partner = follow, lead_status
        if dancer is not None:
            other_team_captain = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                                   User.team == dancer.contestant_info[0].team).first()
            text = f"{dancer.get_full_name()} is no longer dancing with {old_partner.get_full_name()} " \
                   f"({old_partner.contestant_info[0].team}) in {competition}."
            n = Notification(title=f"{dancer.get_full_name()} - no partner in {competition}",
                             text=text.format(dancer=dancer.get_full_name(), comp=competition), user=other_team_captain)
            db.session.add(n)
            db.session.commit()
    return redirect(url_for('teamcaptains.couples_list'))


@bp.route('/partner_request_list', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def partner_request_list():
    requests = PartnerRequest.query.all()
    my_requests = [req for req in requests if req.dancer.contestant_info[0].team == current_user.team]
    other_requests = list(req for req in requests if req.other.contestant_info[0].team == current_user.team and
                          req.state == PartnerRequest.STATE['Open'])
    return render_template('teamcaptains/partner_list.html', my_requests=my_requests, other_requests=other_requests,
                           title='partner requests')


@bp.route('/partner_request', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def partner_request():
    form = PartnerRequestForm()
    dancer_choices = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo)\
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == REGISTERED,
                DancingInfo.partner.is_(None),
                or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                    DancingInfo.level == BEGINNERS))\
        .order_by(Contestant.first_name).all()
    if len(dancer_choices) == 0:
        flash(f"There are currently no dancers registered that require a partner.", 'alert-warning')
        return redirect(url_for('teamcaptains.partner_request_list'))
    other_choices = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(ContestantInfo.team != current_user.team, StatusInfo.status == REGISTERED,
                DancingInfo.partner.is_(None),
                or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                    DancingInfo.level == BEGINNERS)) \
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    form.dancer.choices = map(lambda c: (c.contestant_id, c.get_full_name()), dancer_choices)
    form.other.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                        .format(c.contestant_info[0].team, c.get_full_name())), other_choices)
    form.level.data = BREITENSPORT
    if form.validate_on_submit():
        di1 = DancingInfo.query.filter_by(contestant_id=form.dancer.data, competition=form.competition.data).first()
        if len(PartnerRequest.query.filter(PartnerRequest.dancer_id == form.dancer.data,
                                           PartnerRequest.state == PartnerRequest.STATE['Open']).all()) > 0:
            flash(f"There is already an active request out for {di1.contestant} in {form.competition.data}. "
                  f"Please cancel that request first, before sending out another one.", 'alert-danger')
            return redirect(url_for('teamcaptains.partner_request_list'))
        di2 = DancingInfo.query.filter_by(contestant_id=form.other.data, competition=form.competition.data).first()
        match, errors = di1.valid_match(di2)
        if not match:
            flash("{} and {} are not a valid couple:"
                  .format(di1.contestant.get_full_name(), di2.contestant.get_full_name()), 'alert-danger')
            for e in errors:
                flash(e, 'alert-warning')
            return redirect(url_for('teamcaptains.partner_request'))
        else:
            pr = PartnerRequest(dancer_id=form.dancer.data, other_id=form.other.data, remark=form.remark.data,
                                competition=form.competition.data, level=form.level.data)
            print(pr)
            db.session.add(pr)
            db.session.commit()
            flash('Partner request sent. Please wait until the other teamcaptain has handled the request.')
            return redirect(url_for('teamcaptains.partner_request_list'))
    return render_template('teamcaptains/partner_request.html', form=form, title='partner_request')


@bp.route('/partner_cancel/<req>/', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def partner_cancel(req):
    req = PartnerRequest.query.filter(PartnerRequest.id == req).first()
    req.cancel()
    flash(f'Partner request for {req.dancer} with {req.other} in {req.competition} cancelled.')
    db.session.commit()
    return redirect(url_for('teamcaptains.partner_request_list'))


@bp.route('/partner_request/<req>/', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def request_respond(req):
    req = PartnerRequest.query.filter_by(id=req).first()
    if not req:
        return redirect('errors/404.html')
    if req.other.contestant_info[0].team != current_user.team:
        return redirect('errors/404.html')
    form = PartnerRespondForm()
    if form.validate_on_submit():
        accepted = form.accept.data
        req.response = form.remark.data
        if accepted:
            success = True
            partner = next((p.partner for p in req.other.dancing_info if p.competition == req.competition), None)
            if partner is not None:
                success = False
                flash('{} already has a dancing partner'.format(req.other.get_full_name(), partner))
            partner = next((p.partner for p in req.dancer.dancing_info if p.competition == req.competition), None)
            if partner is not None:
                success = False
                flash('{} already has a dancing partner'.format(req.dancer.get_full_name(), partner))
            if success:
                req.accept()
                flash('Dance partner request accepted')
                db.session.commit()
            else:
                return redirect(url_for('teamcaptains.request_respond', req=req.id))
        else:
            req.reject()
            flash('Dance partner request rejected')
        db.session.commit()
        return redirect(url_for('teamcaptains.partner_request_list'))
    return render_template('teamcaptains/request_respond.html', title="Respond to partner request", form=form,
                           req=req)


@bp.route('/set_teamcaptains', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def set_teamcaptains():
    form = TeamCaptainForm()
    form.number.query = Contestant.query.join(ContestantInfo).join(StatusInfo)\
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == REGISTERED)
    current_tc = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, ContestantInfo.team_captain.is_(True)).first()
    if form.validate_on_submit():
        if form.number.data is not None:
            new_tc = db.session.query(Contestant) \
                .filter(Contestant.contestant_id == form.number.data.contestant_id).first()
            new_tc.contestant_info[0].set_teamcaptain()
            flash('{} has been made teamcaptain.'.format(new_tc.get_full_name()), 'alert-success')
            return redirect(url_for('teamcaptains.set_teamcaptains'))
        else:
            if current_tc is not None:
                current_tc.contestant_info[0].team_captain = False
                db.session.commit()
                flash('Removed {} from teamcaptain function.'.format(current_tc.get_full_name()))
            return redirect(url_for('teamcaptains.set_teamcaptains'))
    return render_template('teamcaptains/set_teamcaptains.html', form=form, current_tc=current_tc)


@bp.route('/raffle_result', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def raffle_result():
    # TODO - PRIORITY - Update page after reworked Check-In page
    ts = TournamentState.query.first()
    if ts.main_raffle_result_visible:
        all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(ContestantInfo.team == current_user.team).order_by(ContestantInfo.number).all()
        selected_dancers = [d for d in all_dancers if d.status_info[0].status == SELECTED]
        confirmed_dancers = [d for d in all_dancers if d.status_info[0].status == CONFIRMED]
        all_leads = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
            .filter(ContestantInfo.team == current_user.team, DancingInfo.role == LEAD) \
            .order_by(DancingInfo.level, ContestantInfo.number).all()
        all_follows = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
            .filter(ContestantInfo.team == current_user.team, DancingInfo.role == FOLLOW) \
            .order_by(DancingInfo.level, ContestantInfo.number).all()

        for follow in all_follows:
            for dance in follow.dancing_info:
                if dance.partner is not None:
                    c = Contestant.query.filter_by(contestant_id=dance.partner).first()
                    if c and c not in all_leads:
                        all_leads.append(c)

        for lead in all_leads:
            for dance in lead.dancing_info:
                if dance.partner is not None:
                    c = Contestant.query.filter_by(contestant_id=dance.partner).first()
                    if c and c not in all_follows:
                        all_follows.append(c)

        ballroom_couples_leads = [dancer for dancer in all_leads if
                                  get_dancing_categories(dancer.dancing_info)[BALLROOM].role == LEAD and
                                  get_dancing_categories(dancer.dancing_info)[BALLROOM].partner is not None]
        ballroom_couples_follows = [dancer for dancer in all_follows if
                                    get_dancing_categories(dancer.dancing_info)[BALLROOM].role == FOLLOW and
                                    get_dancing_categories(dancer.dancing_info)[BALLROOM].partner is not None]
        latin_couples_leads = [dancer for dancer in all_leads if
                               get_dancing_categories(dancer.dancing_info)[LATIN].role == LEAD and
                               get_dancing_categories(dancer.dancing_info)[LATIN].partner is not None]
        latin_couples_follows = [dancer for dancer in all_follows if
                                 get_dancing_categories(dancer.dancing_info)[LATIN].role == FOLLOW and
                                 get_dancing_categories(dancer.dancing_info)[LATIN].partner is not None]
        confirmed_ballroom_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                                      list(itertools.product([dancer for dancer in ballroom_couples_leads if
                                                              dancer.status_info[0].status == CONFIRMED],
                                                             [dancer for dancer in ballroom_couples_follows if
                                                              dancer.status_info[0].status == CONFIRMED])) if
                                      couple[0].contestant_id == get_dancing_categories(
                                          couple[1].dancing_info)[BALLROOM].partner]
        confirmed_latin_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                                   list(itertools.product([dancer for dancer in latin_couples_leads
                                                           if dancer.status_info[0].status == CONFIRMED],
                                                          [dancer for dancer in latin_couples_follows
                                                           if dancer.status_info[0].status == CONFIRMED])) if
                                   couple[0].contestant_id == get_dancing_categories(
                                       couple[1].dancing_info)[LATIN].partner]
        ballroom_lead_blind_daters = [dancer for dancer in all_leads if
                                      get_dancing_categories(dancer.dancing_info)[BALLROOM].role == LEAD and
                                      get_dancing_categories(dancer.dancing_info)[BALLROOM].partner is None and
                                      dancer.status_info[0].status == CONFIRMED]
        ballroom_follow_blind_daters = [dancer for dancer in all_follows if
                                        get_dancing_categories(dancer.dancing_info)[BALLROOM].role == FOLLOW
                                        and get_dancing_categories(dancer.dancing_info)[BALLROOM].partner is None
                                        and dancer.status_info[0].status == CONFIRMED]
        latin_lead_blind_daters = [dancer for dancer in all_leads if
                                   get_dancing_categories(dancer.dancing_info)[LATIN].role == LEAD and
                                   get_dancing_categories(dancer.dancing_info)[LATIN].partner is None and
                                   dancer.status_info[0].status == CONFIRMED]
        latin_follow_blind_daters = [dancer for dancer in all_follows if
                                     get_dancing_categories(dancer.dancing_info)[LATIN].role == FOLLOW and
                                     get_dancing_categories(dancer.dancing_info)[LATIN].partner is None and
                                     dancer.status_info[0].status == CONFIRMED]
        if request.method == 'POST':
            form = request.form
            if 'confirm' in form:
                confirmed_dancers = [d for d in selected_dancers if str(d.contestant_id) in form]
                for dancer in confirmed_dancers:
                    dancer.status_info[0].set_status(CONFIRMED)
                db.session.commit()
                flash('Confirmed selected dancer(s).', 'alert-success')
                return redirect(url_for('teamcaptains.raffle_result'))
        return render_template('teamcaptains/raffle_results.html', data=data, tournament_settings=ts, func=func,
                               selected_dancers=selected_dancers, confirmed_dancers=confirmed_dancers,
                               confirmed_ballroom_couples=confirmed_ballroom_couples,
                               confirmed_latin_couples=confirmed_latin_couples,
                               ballroom_lead_blind_daters=ballroom_lead_blind_daters,
                               ballroom_follow_blind_daters=ballroom_follow_blind_daters,
                               latin_lead_blind_daters=latin_lead_blind_daters,
                               latin_follow_blind_daters=latin_follow_blind_daters)
    return render_template('teamcaptains/raffle_results.html', tournament_settings=ts)


@bp.route('/edit_finances', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain'], ACCESS['treasurer']])
def edit_finances():
    ts = TournamentState.query.first()
    finances, confirmed_dancers, cancelled_dancers, refund_dancers = None, None, None, None
    if ts.main_raffle_result_visible:
        all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(ContestantInfo.team == current_user.team, StatusInfo.payment_required.is_(True)) \
            .order_by(ContestantInfo.number).all()
        confirmed_dancers = [d for d in all_dancers if d.status_info[0].status == CONFIRMED]
        cancelled_dancers = [d for d in all_dancers if d.status_info[0].status == CANCELLED]
        finances = finances_overview(all_dancers)
        team_finances = TeamFinances.query.filter_by(team=current_user.team).first()
        form = request.args
        if 'download_file' in form:
            download_list = [get_total_dancer_price_list(d) for d in all_dancers]
            output = StringIO()
            w = csv.writer(output)
            w.writerow(['Name', 'Amount', 'Description', 'Has paid?'])
            for d in download_list:
                w.writerow(d)
            output.seek(0)
            output = BytesIO(output.read().encode('utf-8-sig'))
            return send_file(output, as_attachment=True,
                             attachment_filename=f"payment_list_{g.sc.tournament}_{g.sc.city}_{g.sc.year}_"
                                                 f"{current_user.team.city}.csv")
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
    else:
        finances, team_finances, confirmed_dancers, cancelled_dancers = None, None, None, None
    return render_template('teamcaptains/edit_finances.html', ts=ts, finances=finances, team_finances=team_finances,
                           confirmed_dancers=confirmed_dancers, cancelled_dancers=cancelled_dancers, data=data)


@bp.route('/bus_to_brno', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def bus_to_brno():
    ts = TournamentState.query.first()
    tc_bus = User.query.join(Team) \
        .filter(User.access == ACCESS['team_captain'], Team.city == "Bielefeld").first()
    add_overview = True if tc_bus.team.name == current_user.team.name else False
    if add_overview:
        included_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo).join(AdditionalInfo) \
            .join(Team).filter(StatusInfo.status == CONFIRMED, AdditionalInfo.bus_to_brno.is_(True)) \
            .order_by(Team.city, ContestantInfo.number).all()
    else:
        included_dancers = None
    if ts.main_raffle_result_visible:
        confirmed_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo).join(AdditionalInfo) \
            .filter(ContestantInfo.team == current_user.team, StatusInfo.status == CONFIRMED) \
            .order_by(ContestantInfo.number).all()
        form = request.args
        if 'download_file' in form:
            output = BytesIO()
            wb = xlsxwriter.Workbook(output, {'in_memory': True})
            ws = wb.add_worksheet(name=datetime.date.today().strftime("%B %d, %Y"))
            ws.write(0, 0, 'Dancer')
            ws.write(0, 1, 'Email')
            ws.write(0, 2, 'Team')
            for c in range(0, len(included_dancers)):
                ws.write(c + 1, 0, included_dancers[c].get_full_name())
                ws.write(c + 1, 1, included_dancers[c].email)
                ws.write(c + 1, 2, included_dancers[c].contestant_info[0].team.city)
            ws.set_column(0, 0, 20)
            ws.set_column(1, 1, 40)
            ws.set_column(2, 2, 30)
            ws.set_column(3, 3, 20)
            wb.close()
            output.seek(0)
            return send_file(output, as_attachment=True, attachment_filename="Bus_to_Brno_dancers.xlsx")
        if request.method == 'POST':
            changes = False
            for dancer in confirmed_dancers:
                if request.form.get(str(dancer.contestant_info[0].number)) is not None:
                    if not dancer.additional_info[0].bus_to_brno:
                        changes = True
                    dancer.additional_info[0].bus_to_brno = True
                else:
                    if dancer.additional_info[0].bus_to_brno:
                        changes = True
                    dancer.additional_info[0].bus_to_brno = False
            if changes:
                db.session.commit()
                flash('Changes saved successfully.', 'alert-success')
            else:
                flash('No changes were made to submit.', 'alert-warning')
            return redirect(url_for('teamcaptains.bus_to_brno'))
    else:
        confirmed_dancers = None
    return render_template('teamcaptains/bus_to_brno.html', ts=ts, data=data, tc_bus=tc_bus,
                           confirmed_dancers=confirmed_dancers, add_overview=add_overview,
                           included_dancers=included_dancers)


@bp.route('/tournament_check_in', methods=['GET'])
@login_required
@requires_access_level([ACCESS['team_captain']])
def tournament_check_in():
    ts = TournamentState.query.first()
    confirmed_dancers = db.session.query(Contestant).join(ContestantInfo, StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == CONFIRMED)\
        .order_by(ContestantInfo.number).all()
    checked_in_dancers = db.session.query(Contestant).join(ContestantInfo, StatusInfo) \
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == CONFIRMED,
                StatusInfo.checked_in.is_(True)).order_by(ContestantInfo.number).all()
    return render_template('teamcaptains/tournament_check_in.html', ts=ts, data=data,
                           confirmed_dancers=confirmed_dancers, checked_in_dancers=checked_in_dancers)
