from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.blind_date_assistant import bp
from ntds_webportal.blind_date_assistant.forms import CreateCoupleForm, CreateCoupleExtraCompetitionForm
from ntds_webportal.models import requires_access_level, Contestant, ContestantInfo, DancingInfo, StatusInfo, \
    SalsaPartners, PolkaPartners
from ntds_webportal.functions import get_dancing_categories, notify_teamcaptains_broken_up_couple, \
    notify_teamcaptains_couple_created
import ntds_webportal.data as data
from ntds_webportal.data import *
import itertools


@bp.route('/create_couple', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[BLIND_DATE_ASSISTANT]])
def create_couple():
    form = CreateCoupleForm()
    leads = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo)\
        .filter(StatusInfo.status == CONFIRMED, DancingInfo.role == LEAD, DancingInfo.partner.is_(None))\
        .order_by(Contestant.first_name).all()
    follows = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo)\
        .filter(StatusInfo.status == CONFIRMED, DancingInfo.role == FOLLOW, DancingInfo.partner.is_(None))\
        .order_by(Contestant.first_name).all()
    form.lead.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                       .format(c.contestant_info.team, c.get_full_name())), leads)
    form.follow.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                         .format(c.contestant_info.team, c.get_full_name())), follows)
    if form.is_submitted():
        if form.validate_on_submit():
            lead = DancingInfo.query.filter_by(contestant_id=form.lead.data, competition=form.competition.data).first()
            follow = DancingInfo.query.filter_by(contestant_id=form.follow.data, competition=form.competition.data)\
                .first()
            match, errors = lead.valid_match(follow, breitensport=False)
            if not match:
                flash("{} and {} are not a valid couple:"
                      .format(lead.contestant.get_full_name(), follow.contestant.get_full_name()), 'alert-danger')
                for e in errors:
                    flash(e, 'alert-warning')
            else:
                lead.set_partner(follow.contestant_id)
                db.session.commit()
                lead = Contestant.query.filter(Contestant.contestant_id == lead.contestant_id).first()
                follow = Contestant.query.filter(Contestant.contestant_id == follow.contestant_id).first()
                flash(f'Created a couple with {lead} and {follow} in {form.competition.data}.', 'alert-success')
                notify_teamcaptains_couple_created(lead, follow, form.competition.data)
            return redirect(url_for('blind_date_assistant.create_couple'))
    all_leads = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo)\
        .filter(StatusInfo.status == CONFIRMED, DancingInfo.role == LEAD)\
        .order_by(DancingInfo.level, ContestantInfo.number).all()
    all_follows = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo)\
        .filter(StatusInfo.status == CONFIRMED, DancingInfo.role == FOLLOW)\
        .order_by(DancingInfo.level, ContestantInfo.number).all()
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
    confirmed_ballroom_couples = [{LEAD: couple[0], FOLLOW: couple[1]} for couple in
                                  list(itertools.product([dancer for dancer in ballroom_couples_leads if
                                                          dancer.status_info.status == CONFIRMED],
                                                         [dancer for dancer in ballroom_couples_follows if
                                                          dancer.status_info.status == CONFIRMED])) if
                                  couple[0].contestant_id == get_dancing_categories(
                                      couple[1].dancing_info)[BALLROOM].partner]
    confirmed_latin_couples = [{LEAD: couple[0], FOLLOW: couple[1]} for couple in
                               list(itertools.product([dancer for dancer in latin_couples_leads
                                                       if dancer.status_info.status == CONFIRMED],
                                                      [dancer for dancer in latin_couples_follows
                                                       if dancer.status_info.status == CONFIRMED])) if
                               couple[0].contestant_id == get_dancing_categories(
                                   couple[1].dancing_info)[LATIN].partner]
    return render_template('blind_date_assistant/create_couple.html', data=data, form=form,
                           confirmed_ballroom_couples=confirmed_ballroom_couples,
                           confirmed_latin_couples=confirmed_latin_couples)


@bp.route('/break_up_couple/<competition>/<couple_lead>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[BLIND_DATE_ASSISTANT]])
def break_up_couple(couple_lead, competition):
    lead = DancingInfo.query.filter_by(contestant_id=couple_lead, competition=competition)\
        .first()
    follow = lead.partner
    lead.set_partner(None)
    db.session.commit()
    lead = Contestant.query.filter(Contestant.contestant_id == couple_lead).first()
    follow = Contestant.query.filter(Contestant.contestant_id == follow).first()
    notify_teamcaptains_broken_up_couple(lead=lead, follow=follow, competition=competition)
    flash(f'{lead} and {follow} are not a couple anymore in {competition}.')
    return redirect(url_for('blind_date_assistant.create_couple'))


@bp.route('/create_couple_salsa', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[BLIND_DATE_ASSISTANT]])
def create_couple_salsa():
    form = CreateCoupleExtraCompetitionForm()
    dancers = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(StatusInfo.status == CONFIRMED).order_by(Contestant.first_name).all()
    salsa_couples = SalsaPartners.query.all()
    salsa_dancers = []
    for couple in salsa_couples:
        salsa_dancers.append(couple.lead_id)
        salsa_dancers.append(couple.follow_id)
    dancers = [d for d in dancers if d.contestant_id not in salsa_dancers]
    form.lead.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                       .format(c.get_full_name(), c.contestant_info.team)), dancers)
    form.follow.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                         .format(c.get_full_name(), c.contestant_info.team)), dancers)
    salsa_couples = [{'id': c.couple_id,
                      LEAD: Contestant.query.filter(Contestant.contestant_id == c.lead_id).first().get_full_name(),
                      FOLLOW: Contestant.query.filter(Contestant.contestant_id == c.follow_id).first().get_full_name()}
                     for c in salsa_couples]
    salsa_couples.sort(key=lambda x: x[LEAD])
    if form.validate_on_submit():
        lead = Contestant.query.filter_by(contestant_id=form.lead.data).first()
        follow = Contestant.query.filter_by(contestant_id=form.follow.data).first()
        if lead.contestant_id != follow.contestant_id:
            couple = SalsaPartners()
            couple.lead_id = lead.contestant_id
            couple.follow_id = follow.contestant_id
            db.session.add(couple)
            db.session.commit()
            flash(f'Created a couple with {lead} and {follow} for {SALSA}.', 'alert-success')
            notify_teamcaptains_couple_created(lead, follow, SALSA)
            return redirect(url_for('blind_date_assistant.create_couple_salsa'))
        else:
            flash(f'Really?', 'alert-warning')
            return redirect(url_for('blind_date_assistant.create_couple_salsa'))
    return render_template('blind_date_assistant/create_couple_salsa.html', form=form, data=data,
                           salsa_couples=salsa_couples)


@bp.route('/break_up_salsa_couple/<couple_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[BLIND_DATE_ASSISTANT]])
def break_up_salsa_couple(couple_id):
    couple = SalsaPartners.query.filter(SalsaPartners.couple_id == couple_id).first()
    lead = Contestant.query.filter_by(contestant_id=couple.lead_id).first()
    follow = Contestant.query.filter_by(contestant_id=couple.follow_id).first()
    db.session.delete(couple)
    db.session.commit()
    flash(f'{lead} and {follow} are no longer dancing {SALSA} together.', 'alert-info')
    notify_teamcaptains_broken_up_couple(lead=lead, follow=follow, competition=SALSA)
    return redirect(url_for('blind_date_assistant.create_couple_salsa'))


@bp.route('/create_couple_polka', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[BLIND_DATE_ASSISTANT]])
def create_couple_polka():
    form = CreateCoupleExtraCompetitionForm()
    dancers = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(StatusInfo.status == CONFIRMED).order_by(Contestant.first_name).all()
    polka_couples = PolkaPartners.query.all()
    polka_dancers = []
    for couple in polka_couples:
        polka_dancers.append(couple.lead_id)
        polka_dancers.append(couple.follow_id)
    dancers = [d for d in dancers if d.contestant_id not in polka_dancers]
    form.lead.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                       .format(c.get_full_name(), c.contestant_info.team)), dancers)
    form.follow.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                         .format(c.get_full_name(), c.contestant_info.team)), dancers)
    polka_couples = [{'id': c.couple_id,
                      LEAD: Contestant.query.filter(Contestant.contestant_id == c.lead_id).first().get_full_name(),
                      FOLLOW: Contestant.query.filter(Contestant.contestant_id == c.follow_id).first().get_full_name()}
                     for c in polka_couples]
    polka_couples.sort(key=lambda x: x[LEAD])
    if form.validate_on_submit():
        lead = Contestant.query.filter_by(contestant_id=form.lead.data).first()
        follow = Contestant.query.filter_by(contestant_id=form.follow.data).first()
        if lead.contestant_id != follow.contestant_id:
            couple = PolkaPartners()
            couple.lead_id = lead.contestant_id
            couple.follow_id = follow.contestant_id
            db.session.add(couple)
            db.session.commit()
            flash(f'Created a couple with {lead} and {follow} for {POLKA}.', 'alert-success')
            notify_teamcaptains_couple_created(lead, follow, POLKA)
            return redirect(url_for('blind_date_assistant.create_couple_polka'))
        else:
            flash(f'Really?', 'alert-warning')
            return redirect(url_for('blind_date_assistant.create_couple_polka'))
    return render_template('blind_date_assistant/create_couple_polka.html', form=form, data=data,
                           polka_couples=polka_couples)


@bp.route('/break_up_polka_couple/<couple_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[BLIND_DATE_ASSISTANT]])
def break_up_polka_couple(couple_id):
    couple = PolkaPartners.query.filter(PolkaPartners.couple_id == couple_id).first()
    lead = Contestant.query.filter_by(contestant_id=couple.lead_id).first()
    follow = Contestant.query.filter_by(contestant_id=couple.follow_id).first()
    db.session.delete(couple)
    db.session.commit()
    flash(f'{lead} and {follow} are no longer dancing {POLKA} together.', 'alert-info')
    notify_teamcaptains_broken_up_couple(lead=lead, follow=follow, competition=POLKA)
    return redirect(url_for('blind_date_assistant.create_couple_polka'))
