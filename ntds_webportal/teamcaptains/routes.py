from flask import render_template, url_for, redirect, flash, request, send_file, g, Markup, jsonify, json
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.teamcaptains import bp
from ntds_webportal.teamcaptains.forms import RegisterContestantForm, EditContestantForm, TeamCaptainForm, \
    PartnerRequestForm, PartnerRespondForm, NameChangeRequestForm, CreateCoupleForm, ResendCredentialsForm, \
    CheckEmailForm
from ntds_webportal.teamcaptains.email import send_dancer_user_account_email
from ntds_webportal.models import User, requires_access_level, Contestant, ContestantInfo, DancingInfo, \
    StatusInfo, PartnerRequest, NameChangeRequest, TournamentState, Notification, AdditionalInfo, Team, \
    requires_tournament_state, Competition
from ntds_webportal.functions import get_dancing_categories, submit_contestant, random_password
import ntds_webportal.functions as func
from ntds_webportal.data import *
from ntds_webportal.helper_classes import TeamPossiblePartners
from sqlalchemy import and_, or_
import itertools
import datetime
import xlsxwriter
from io import BytesIO, StringIO
import csv


def create_dancer_user_account(contestant):
    dancer_account = User()
    dancer_account.team = current_user.team
    dancer_account.username = contestant.email
    dancer_account.email = contestant.email
    dancer_account_password = random_password()
    dancer_account.set_password(dancer_account_password)
    dancer_account.access = ACCESS[DANCER]
    dancer_account.is_active = True
    dancer_account.send_new_messages_email = True
    dancer_account.dancer = contestant
    db.session.add(dancer_account)
    db.session.commit()
    send_dancer_user_account_email(dancer_account, contestant.get_full_name(), dancer_account_password)


@bp.route('/register_dancers', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_OPEN)
def register_dancers():
    if not g.ts.registration_open:
        flash(REGISTRATION_NOT_OPEN_TEXT)
        return redirect(url_for('main.dashboard'))
    form = RegisterContestantForm()
    if request.method == POST:
        form.custom_validate()
        if form.validate_on_submit():
            contestant = submit_contestant(form)
            flash(f'{contestant.get_full_name()} has been registered successfully.', 'alert-success')
            create_dancer_user_account(contestant)
            return redirect(url_for('teamcaptains.register_dancers'))
        else:
            if form.is_submitted():
                flash('Not all fields of the form have been filled in (correctly).', 'alert-danger')
    possible_partners = TeamPossiblePartners(current_user, include_gdpr=True).possible_partners()
    return render_template('teamcaptains/register_dancers.html', form=form, possible_partners=possible_partners)


@bp.route('/check_email', methods=['POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_OPEN)
def check_email():
    form = CheckEmailForm()
    email = json.loads(request.data)
    form.email.data = email
    form.validate()
    data = {"error": ""}
    if len(form.email.errors) > 0:
        data["error"] = form.email.errors[0]
    return jsonify(data)


@bp.route('/validate_registration_field', methods=['POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_OPEN)
def validate_registration_field():
    form = RegisterContestantForm()
    field = json.loads(request.data)
    getattr(form, field["name"]).data = field["fieldValue"]
    form.validate()
    field = form.react(field["name"])
    return jsonify(field)


@bp.route('/edit_dancers', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def edit_dancers():
    if not current_user.has_dancers_registered():
        flash("Cannot enter page. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    wide = request.args.get('wide', 0, type=int)
    dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team).order_by(Contestant.first_name).all()
    order = [NO_GDPR, CONFIRMED, SELECTED, REGISTERED, CANCELLED]
    dancers = sorted(dancers, key=lambda o: order.index(o.status_info.status))
    return render_template('teamcaptains/edit_dancers.html', dancers=dancers, wide=wide)


@bp.route('/edit_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def edit_dancer(number):
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    wide = int(request.values['wide'])
    dancer = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, Contestant.contestant_id == number) \
        .order_by(Contestant.contestant_id).first_or_404()
    possible_partners = TeamPossiblePartners(current_user, dancer=dancer, include_gdpr=True).possible_partners()
    form = EditContestantForm(dancer)
    # TEMP FIX
    form.first_name.validators = []
    form.last_name.validators = []
    if request.method == GET:
        form.populate(dancer)
    if request.method == POST:
        form.custom_validate(dancer)
    if form.validate_on_submit():
        dancer.status_info.feedback_about_information = None
        db.session.commit()
        flash('{} data has been changed successfully.'.format(submit_contestant(form, contestant=dancer)),
              'alert-success')
        return redirect(url_for('teamcaptains.edit_dancers', wide=wide))
    if dancer.status_info.feedback_about_information is not None:
        flash(Markup(f'{dancer.get_full_name()} sent feedback about his/her submitted information:<br/>'
                     f'{dancer.status_info.feedback_about_information}<br/><br/> You can remove this notification '
                     f'by saving the form on this page.'), 'alert-info')
    return render_template('teamcaptains/edit_dancer.html', dancer=dancer, form=form, wide=wide,
                           possible_partners=possible_partners)


@bp.route('/register_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def register_dancer(number):
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    register = request.args.get('register', None, type=int)
    changed_dancer = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, Contestant.contestant_id == number).first()
    if register == 0:
        status = changed_dancer.status_info.status
        changed_dancer.cancel_registration()
        db.session.commit()
        flash('The registration of {} has been cancelled.'.format(changed_dancer.get_full_name()), 'alert-info')
        text = f"{changed_dancer.get_full_name()} from team {changed_dancer.contestant_info.team.name} " \
               f"has cancelled his/her registration.\n"
        title = f"Cancelled registration, previously {status} " \
            f"- {changed_dancer.get_full_name()} ({changed_dancer.contestant_info.team})"
        n = Notification(title=title, text=text, user=User.query.filter(User.access == ACCESS[ORGANIZER]).first())
        n.send()
    elif register == 1:
        changed_dancer.status_info.set_status(REGISTERED)
        db.session.commit()
        flash('{} has been re-registered successfully.'.format(changed_dancer.get_full_name()), 'alert-success')
    return redirect(url_for('teamcaptains.edit_dancers', wide=int(request.values['wide'])))


@bp.route('/delete_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def delete_dancer(number):
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    changed_dancer = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, Contestant.contestant_id == number).first()
    dancer_account = User.query.filter(User.dancer == changed_dancer).first()
    if changed_dancer.status_info.status == NO_GDPR or changed_dancer.status_info.status == CANCELLED:
        if dancer_account is not None:
            if changed_dancer.deletable():
                if changed_dancer.status_info.status == NO_GDPR:
                    changed_dancer.cancel_registration()
                db.session.delete(dancer_account)
                db.session.commit()
                flash(f"Permanently deleted the registration data of {changed_dancer.get_full_name()}.")
            else:
                flash(f"Cannot permanently delete the registration data of {changed_dancer.get_full_name()}. "
                      f"{changed_dancer.first_name} either needs to receive merchandise, needs to pay, "
                      f"or has a refund pending.")
    else:
        flash("Can only delete a dancers' account if the dancer has not accepted the GDPR or if the dancers' "
              "registration is cancelled.")
    return redirect(url_for('teamcaptains.edit_dancers', wide=int(request.values['wide'])))


@bp.route('/resend_login_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def resend_login_dancer(number):
    changed_dancer = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, Contestant.contestant_id == number).first()
    if changed_dancer.status_info.status != NO_GDPR:
        flash('Cannot reset the login credentials of a dancer that has accepted the GDPR.', 'alert-warning')
        return redirect(url_for('teamcaptains.edit_dancers'))
    form = ResendCredentialsForm()
    if request.method == GET:
        form.populate(changed_dancer)
    if form.validate_on_submit():
        all_dancers = Contestant.query.filter(Contestant.contestant_id != changed_dancer.contestant_id).all()
        if len([d for d in all_dancers if d.email == form.email.data]) == 0:
            changed_dancer.email = form.email.data
            changed_dancer.user.email = form.email.data
            changed_dancer.user.username = form.email.data
            dancer_account_password = random_password()
            changed_dancer.user.set_password(dancer_account_password)
            db.session.commit()
            send_dancer_user_account_email(changed_dancer.user, changed_dancer.get_full_name(), dancer_account_password)
            flash(f'New login credentials have been sent '
                  f'to {changed_dancer.get_full_name()} at {changed_dancer.email}.', 'alert-success')
            return redirect(url_for('teamcaptains.edit_dancers'))
        else:
            flash(f'Someone is already registered with {form.email.data} as their e-mail address.')
    return render_template('teamcaptains/resend_login_dancer.html', form=form, dancer=changed_dancer)


@bp.route('/name_change_request/<contestant>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def name_change_request(contestant):
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    wide = int(request.values['wide'])
    contestant = Contestant.query.filter_by(contestant_id=contestant).first()
    if not contestant or not contestant.contestant_info.team == current_user.team:
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
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def couples_list():
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
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
                        couple['lead'].contestant_info.team == current_user.team
                        or couple['follow'].contestant_info.team == current_user.team]
    latin_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                     list(itertools.product(latin_couples_leads, latin_couples_follows)) if
                     couple[0].contestant_id == get_dancing_categories(couple[1].dancing_info)[LATIN].partner]
    latin_couples = [couple for couple in latin_couples if couple['lead'].contestant_info.team == current_user.team
                     or couple['follow'].contestant_info.team == current_user.team]
    return render_template('teamcaptains/couples_lists.html', func=func,
                           ballroom_couples=ballroom_couples, latin_couples=latin_couples)


@bp.route('/create_couple', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def create_couple():
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    form = CreateCoupleForm(g.sc)
    leads = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo)\
        .filter(ContestantInfo.team == current_user.team,
                or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR),
                DancingInfo.role == LEAD, DancingInfo.partner.is_(None),
                or_(and_(DancingInfo.level == BREITENSPORT,
                         or_(DancingInfo.blind_date.is_(False),
                             DancingInfo.blind_date.is_(not g.sc.breitensport_obliged_blind_date))),
                    DancingInfo.level == BEGINNERS)).order_by(Contestant.first_name)
    follows = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(ContestantInfo.team == current_user.team,
                or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR),
                DancingInfo.role == FOLLOW, DancingInfo.partner.is_(None),
                or_(and_(DancingInfo.level == BREITENSPORT,
                         or_(DancingInfo.blind_date.is_(False),
                             DancingInfo.blind_date.is_(not g.sc.breitensport_obliged_blind_date))),
                    DancingInfo.level == BEGINNERS)).order_by(Contestant.first_name)
    if len(leads.all()) == 0 or len(follows.all()) == 0:
        flash(f"There are currently {len(leads.all())} available Leads and {len(follows.all())} available Follows "
              f"registered. Cannot create new couples.", 'alert-warning')
        return redirect(url_for('teamcaptains.couples_list'))
    possible_partners = TeamPossiblePartners(current_user, include_gdpr=True).possible_partners()
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
    return render_template('teamcaptains/create_couple.html', form=form, possible_partners=possible_partners)


@bp.route('/break_up_couple/<competition>,<lead_id>,<follow_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def break_up_couple(competition, lead_id, follow_id):
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    lead = DancingInfo.query.filter(DancingInfo.competition == competition, DancingInfo.contestant_id == lead_id,
                                    DancingInfo.partner == follow_id).first()
    follow = Contestant.query.filter(Contestant.contestant_id == follow_id).first()
    lead_status = Contestant.query.filter(Contestant.contestant_id == lead_id).first()
    if lead_status.status_info.status == SELECTED or lead_status.status_info.status == CONFIRMED \
            or follow.status_info.status == SELECTED or follow.status_info.status == CONFIRMED:
        flash(f"Cannot break up a couple that has been {SELECTED} or {CONFIRMED}.")
    else:
        lead.set_partner(None)
        db.session.commit()
        flash(f'{lead.contestant} and {follow} are not a couple anymore in {competition}.')
        dancer, old_partner = None, None
        if lead_status.contestant_info.team != current_user.team:
            dancer, old_partner = lead_status, follow
        elif follow.contestant_info.team != current_user.team:
            dancer, old_partner = follow, lead_status
        if dancer is not None:
            other_team_captain = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                                   User.team == dancer.contestant_info.team).first()
            text = f"{dancer.get_full_name()} is no longer dancing with {old_partner.get_full_name()} " \
                   f"({old_partner.contestant_info.team}) in {competition}."
            n = Notification(title=f"{dancer.get_full_name()} - no partner in {competition}",
                             text=text.format(dancer=dancer.get_full_name(), comp=competition), user=other_team_captain)
            n.send()
    return redirect(url_for('teamcaptains.couples_list'))


@bp.route('/partner_request_list', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def partner_request_list():
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    requests = PartnerRequest.query.all()
    my_requests = [req for req in requests if req.dancer.contestant_info.team == current_user.team]
    other_requests = list(req for req in requests if req.other.contestant_info.team == current_user.team)
    return render_template('teamcaptains/partner_list.html', my_requests=my_requests, other_requests=other_requests,
                           title='partner requests')


@bp.route('/partner_request', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def partner_request():
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))

    dancer_choices = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo)\
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == REGISTERED,
                DancingInfo.partner.is_(None),
                or_(and_(DancingInfo.level == BREITENSPORT,
                         or_(DancingInfo.blind_date.is_(False),
                             DancingInfo.blind_date.is_(not g.sc.breitensport_obliged_blind_date))),
                    DancingInfo.level == BEGINNERS)).order_by(Contestant.first_name)
    if len(dancer_choices.all()) == 0:
        flash(f"There are currently no dancers registered in your team that require a partner.", 'alert-warning')
        flash(f"Dancers that have not accepted the GDPR yet, cannot be used for a partner request, as this would mean "
              f"sharing some of their personal data. Once the GDPR has been accepted, dancers are available for a "
              f"partner request")
        return redirect(url_for('teamcaptains.partner_request_list'))
    other_choices = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(ContestantInfo.team != current_user.team, StatusInfo.status == REGISTERED,
                DancingInfo.partner.is_(None),
                or_(and_(DancingInfo.level == BREITENSPORT,
                         or_(DancingInfo.blind_date.is_(False),
                             DancingInfo.blind_date.is_(not g.sc.breitensport_obliged_blind_date))),
                    DancingInfo.level == BEGINNERS)) \
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    if len(other_choices) == 0:
        flash(f"There are currently no dancers registered in the other teams that require a partner.", 'alert-warning')
        return redirect(url_for('teamcaptains.partner_request_list'))
    form = PartnerRequestForm(g.sc, other_choices)
    form.dancer.query = dancer_choices
    my_dancers = TeamPossiblePartners(current_user).possible_partners()
    possible_partners = TeamPossiblePartners(current_user, other_teams=True).possible_partners()
    if form.validate_on_submit():
        di1 = DancingInfo.query.filter_by(contestant_id=form.dancer.data.contestant_id,
                                          competition=form.competition.data).first()
        if len(PartnerRequest.query.filter(PartnerRequest.dancer_id == form.dancer.data.contestant_id,
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
            pr = PartnerRequest(dancer_id=form.dancer.data.contestant_id, other_id=form.other.data,
                                remark=form.remark.data, competition=form.competition.data, level=form.level.data)
            db.session.add(pr)
            db.session.commit()
            flash('Partner request sent. Please wait until the other teamcaptain has handled the request.')
            return redirect(url_for('teamcaptains.partner_request_list'))
    return render_template('teamcaptains/partner_request.html', form=form, title='partner_request',
                           my_dancers=my_dancers, possible_partners=possible_partners)


@bp.route('/partner_cancel/<req>/', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def partner_cancel(req):
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    req = PartnerRequest.query.filter(PartnerRequest.id == req).first()
    req.cancel()
    flash(f'Partner request for {req.dancer} with {req.other} in {req.competition} cancelled.')
    db.session.commit()
    return redirect(url_for('teamcaptains.partner_request_list'))


@bp.route('/partner_request/<req>/', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def request_respond(req):
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    req = PartnerRequest.query.filter_by(id=req).first()
    if not req:
        return redirect('errors/404.html')
    if req.other.contestant_info.team != current_user.team:
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
    return render_template('teamcaptains/request_respond.html', title="Respond to partner request", form=form, req=req)


@bp.route('/set_teamcaptains', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(REGISTRATION_STARTED)
def set_teamcaptains():
    if not current_user.has_dancers_registered():
        flash("Cannot enter page right now. Register at least one dancer first to access the page.")
        return redirect(url_for('main.dashboard'))
    form = TeamCaptainForm()
    tc_query = Contestant.query.join(ContestantInfo).join(StatusInfo)\
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status != CANCELLED)\
        .order_by(Contestant.first_name)
    form.team_captain_one.query = tc_query
    form.team_captain_two.query = tc_query
    current_tcs = db.session.query(Contestant).join(ContestantInfo) \
        .filter(ContestantInfo.team == current_user.team, ContestantInfo.team_captain.is_(True)).all()
    if request.method == 'GET':
        if len(current_tcs) > 0:
            form.team_captain_one.data = current_tcs[0]
        if len(current_tcs) == 2:
            form.team_captain_two.data = current_tcs[1]
    if form.validate_on_submit():
        current_tc_one = None
        current_tc_two = None
        if current_tcs is not None:
            if len(current_tcs) >= 1:
                current_tc_one = current_tcs[0]
                current_tc_one.contestant_info.team_captain = False
            if len(current_tcs) == 2:
                current_tc_two = current_tcs[1]
                current_tc_two.contestant_info.team_captain = False
            db.session.commit()
        first_team_captain = None
        second_team_captain = None
        if form.team_captain_one.data is not None:
            first_team_captain = form.team_captain_one.data
            first_team_captain.contestant_info.team_captain = True
        if form.team_captain_two.data is not None:
            second_team_captain = form.team_captain_two.data
            second_team_captain.contestant_info.team_captain = True
        db.session.commit()
        if first_team_captain is not None and second_team_captain is not None:
            if first_team_captain in current_tcs and second_team_captain not in current_tcs:
                flash(f"Set {second_team_captain.get_full_name()} as team captain.")
            if first_team_captain not in current_tcs and second_team_captain in current_tcs:
                flash(f"Set {first_team_captain.get_full_name()} as team captain.")
            if first_team_captain not in current_tcs and second_team_captain not in current_tcs:
                flash(f"Set {first_team_captain.get_full_name()} and {second_team_captain.get_full_name()} as "
                      f"team captains.")
        if first_team_captain is not None and second_team_captain is None:
            if first_team_captain not in current_tcs:
                flash(f"Set {first_team_captain.get_full_name()} as team captain.")
            if current_tc_two is not None:
                flash(f"Removed {current_tc_two.get_full_name()} as team captain.")
        if first_team_captain is None and second_team_captain is None:
            if current_tc_one is not None and current_tc_two is not None:
                flash(f"Removed {current_tc_one.get_full_name()} and {current_tc_two.get_full_name()} as "
                      f"team captains.")
            if current_tc_one is not None and current_tc_two is None:
                flash(f"Removed {current_tc_one.get_full_name()} as team captain.")
        return redirect(url_for('teamcaptains.set_teamcaptains'))
    return render_template('teamcaptains/set_teamcaptains.html', form=form, current_tcs=current_tcs)


@bp.route('/raffle_result', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def raffle_result():
    ts = TournamentState.query.first()
    if ts.main_raffle_result_visible:
        all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(ContestantInfo.team == current_user.team).order_by(ContestantInfo.number).all()
        selected_dancers = [d for d in all_dancers if d.status_info.status == SELECTED]
        confirmed_dancers = [d for d in all_dancers if d.status_info.status == CONFIRMED]
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
                                                              dancer.status_info.status == CONFIRMED],
                                                             [dancer for dancer in ballroom_couples_follows if
                                                              dancer.status_info.status == CONFIRMED])) if
                                      couple[0].contestant_id == get_dancing_categories(
                                          couple[1].dancing_info)[BALLROOM].partner]
        confirmed_latin_couples = [{'lead': couple[0], 'follow': couple[1]} for couple in
                                   list(itertools.product([dancer for dancer in latin_couples_leads
                                                           if dancer.status_info.status == CONFIRMED],
                                                          [dancer for dancer in latin_couples_follows
                                                           if dancer.status_info.status == CONFIRMED])) if
                                   couple[0].contestant_id == get_dancing_categories(
                                       couple[1].dancing_info)[LATIN].partner]
        ballroom_lead_blind_daters = [dancer for dancer in all_leads if
                                      get_dancing_categories(dancer.dancing_info)[BALLROOM].role == LEAD and
                                      get_dancing_categories(dancer.dancing_info)[BALLROOM].partner is None and
                                      dancer.status_info.status == CONFIRMED]
        ballroom_follow_blind_daters = [dancer for dancer in all_follows if
                                        get_dancing_categories(dancer.dancing_info)[BALLROOM].role == FOLLOW
                                        and get_dancing_categories(dancer.dancing_info)[BALLROOM].partner is None
                                        and dancer.status_info.status == CONFIRMED]
        latin_lead_blind_daters = [dancer for dancer in all_leads if
                                   get_dancing_categories(dancer.dancing_info)[LATIN].role == LEAD and
                                   get_dancing_categories(dancer.dancing_info)[LATIN].partner is None and
                                   dancer.status_info.status == CONFIRMED]
        latin_follow_blind_daters = [dancer for dancer in all_follows if
                                     get_dancing_categories(dancer.dancing_info)[LATIN].role == FOLLOW and
                                     get_dancing_categories(dancer.dancing_info)[LATIN].partner is None and
                                     dancer.status_info.status == CONFIRMED]
        if request.method == 'POST':
            form = request.form
            if 'confirm' in form:
                confirmed_dancers = [d for d in selected_dancers if str(d.contestant_id) in form]
                for dancer in confirmed_dancers:
                    dancer.status_info.set_status(CONFIRMED)
                db.session.commit()
                flash('Confirmed selected dancer(s).', 'alert-success')
                return redirect(url_for('teamcaptains.raffle_result'))
        return render_template('teamcaptains/raffle_results.html', func=func,
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
@requires_access_level([ACCESS[TEAM_CAPTAIN], ACCESS[TREASURER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def edit_finances():
    if g.ts.main_raffle_result_visible:
        all_dancers = Contestant.query.join(ContestantInfo).join(StatusInfo) \
            .filter(ContestantInfo.team == current_user.team, StatusInfo.payment_required.is_(True)) \
            .order_by(Contestant.first_name).all()
        if request.method == "POST":
            if "download_file" in request.form:
                download_list = [d.payment_csv_string() for d in all_dancers]
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
    return render_template('teamcaptains/edit_finances.html')


@bp.route('/treasurer_inaccessible', methods=['GET'])
@login_required
@requires_access_level([ACCESS[TREASURER]])
def treasurer_inaccessible():
    return render_template('teamcaptains/treasurer_inaccessible.html')


@bp.route('/bus_to_brno', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def bus_to_brno():
    tc_bus = User.query.join(Team) \
        .filter(User.access == ACCESS[TEAM_CAPTAIN], Team.city == "Bielefeld").first()
    add_overview = True if tc_bus.team.name == current_user.team.name else False
    if add_overview:
        included_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo).join(AdditionalInfo) \
            .join(Team).filter(StatusInfo.status == CONFIRMED, AdditionalInfo.bus_to_brno.is_(True)) \
            .order_by(Team.city, ContestantInfo.number).all()
    else:
        included_dancers = None
    if g.ts.main_raffle_result_visible:
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
                ws.write(c + 1, 2, included_dancers[c].contestant_info.team.city)
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
                if request.form.get(str(dancer.contestant_info.number)) is not None:
                    if not dancer.additional_info.bus_to_brno:
                        changes = True
                    dancer.additional_info.bus_to_brno = True
                else:
                    if dancer.additional_info.bus_to_brno:
                        changes = True
                    dancer.additional_info.bus_to_brno = False
            if changes:
                db.session.commit()
                flash('Changes saved successfully.', 'alert-success')
            else:
                flash('No changes were made to submit.', 'alert-warning')
            return redirect(url_for('teamcaptains.bus_to_brno'))
    else:
        confirmed_dancers = None
    return render_template('teamcaptains/bus_to_brno.html', ts=g.ts, data=g.data, tc_bus=tc_bus,
                           confirmed_dancers=confirmed_dancers, add_overview=add_overview,
                           included_dancers=included_dancers)


@bp.route('/tournament_check_in', methods=['GET'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def tournament_check_in():
    dancers = {d.contestant_id: d.json() for d in current_user.team.check_in_dancers()}
    return render_template('teamcaptains/tournament_check_in.html', dancers=dancers)


@bp.route('/starting_lists', methods=['GET'])
@login_required
@requires_access_level([ACCESS[TEAM_CAPTAIN]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def starting_lists():
    contestants = Contestant.query.join(ContestantInfo, StatusInfo)\
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == CONFIRMED).all()
    competitions = Competition.query.all()
    competitions = {c: [] for c in competitions}
    all_competition_dancers = []
    for contestant in contestants:
        for d in contestant.dancers:
            couples = d.couples()
            for c in couples:
                for comp in c.competitions:
                    if c not in competitions[comp]:
                        competitions[comp].append(c)
                        if c.lead.contestant.contestant_info.team == current_user.team:
                            all_competition_dancers.append(c.lead.contestant)
                        if c.follow.contestant.contestant_info.team == current_user.team:
                            all_competition_dancers.append(c.follow.contestant)
            for comp in d.competitions():
                if d not in competitions[comp]:
                    competitions[comp].append(d)
                    all_competition_dancers.append(contestant)
    competitions = {c: sorted(competitions[c], key=lambda x: x.number)
                    for c in competitions if len(competitions[c]) > 0}
    all_dancers = DancingInfo.query.join(StatusInfo, DancingInfo.contestant_id == StatusInfo.contestant_id) \
        .join(ContestantInfo, DancingInfo.contestant_id == ContestantInfo.contestant_id) \
        .filter(ContestantInfo.team == current_user.team, StatusInfo.status == CONFIRMED,
                DancingInfo.level != NO).all()
    competitions = {c: competitions[c] for c in competitions if c.dancing_class.name != TEST}
    return render_template('teamcaptains/starting_lists.html', contestants=contestants, competitions=competitions,
                           all_dancers=all_dancers, all_competition_dancers=all_competition_dancers)
