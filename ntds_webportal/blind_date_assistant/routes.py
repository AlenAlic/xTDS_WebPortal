from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.blind_date_assistant import bp
from ntds_webportal.blind_date_assistant.forms import CreateCoupleForm, CreateCoupleExtraCompetitionForm
from ntds_webportal.models import requires_access_level, Contestant, ContestantInfo, DancingInfo, StatusInfo, \
    SalsaPartners, PolkaPartners
import ntds_webportal.data as data
from ntds_webportal.data import *


@bp.route('/create_couple', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['blind_date_organizer']])
def create_couple():
    form = CreateCoupleForm()
    leads = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(StatusInfo.status == CONFIRMED, DancingInfo.role == LEAD, DancingInfo.partner.is_(None),
                DancingInfo.level == BREITENSPORT)\
        .order_by(Contestant.first_name).all()
    follows = db.session.query(Contestant).join(ContestantInfo).join(DancingInfo).join(StatusInfo) \
        .filter(StatusInfo.status == CONFIRMED, DancingInfo.role == FOLLOW, DancingInfo.partner.is_(None),
                DancingInfo.level == BREITENSPORT)\
        .order_by(Contestant.first_name).all()
    form.lead.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                       .format(c.contestant_info[0].team, c.get_full_name())), leads)
    form.follow.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                         .format(c.contestant_info[0].team, c.get_full_name())), follows)
    if form.validate_on_submit():
        lead = DancingInfo.query.filter_by(contestant_id=form.lead.data, competition=form.competition.data).first()
        follow = DancingInfo.query.filter_by(contestant_id=form.follow.data, competition=form.competition.data).first()
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
        return redirect(url_for('blind_date_assistant.create_couple'))
    return render_template('blind_date_assistant/create_couple.html', form=form)


@bp.route('/create_couple_salsa', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['blind_date_organizer']])
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
                                       .format(c.contestant_info[0].team, c.get_full_name())), dancers)
    form.follow.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                         .format(c.contestant_info[0].team, c.get_full_name())), dancers)
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
            return redirect(url_for('blind_date_assistant.create_couple_salsa'))
        else:
            flash(f'Really?', 'alert-warning')
            return redirect(url_for('blind_date_assistant.create_couple_salsa'))
    return render_template('blind_date_assistant/create_couple_salsa.html', form=form, data=data,
                           salsa_couples=salsa_couples)


@bp.route('/break_up_salsa_couple/<couple_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['blind_date_organizer']])
def break_up_salsa_couple(couple_id):
    couple = SalsaPartners.query.filter(SalsaPartners.couple_id == couple_id).first()
    lead = Contestant.query.filter_by(contestant_id=couple.lead_id).first().get_full_name()
    follow = Contestant.query.filter_by(contestant_id=couple.follow_id).first().get_full_name()
    db.session.delete(couple)
    db.session.commit()
    flash(f'{lead} and {follow} are no longer dancing {SALSA} together.', 'alert-info')
    return redirect(url_for('blind_date_assistant.create_couple_salsa'))


@bp.route('/create_couple_polka', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['blind_date_organizer']])
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
                                       .format(c.contestant_info[0].team, c.get_full_name())), dancers)
    form.follow.choices = map(lambda c: (c.contestant_id, "{} - {}"
                                         .format(c.contestant_info[0].team, c.get_full_name())), dancers)
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
            return redirect(url_for('blind_date_assistant.create_couple_polka'))
        else:
            flash(f'Really?', 'alert-warning')
            return redirect(url_for('blind_date_assistant.create_couple_polka'))
    return render_template('blind_date_assistant/create_couple_polka.html', form=form, data=data,
                           polka_couples=polka_couples)


@bp.route('/break_up_polka_couple/<couple_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['blind_date_organizer']])
def break_up_polka_couple(couple_id):
    couple = PolkaPartners.query.filter(PolkaPartners.couple_id == couple_id).first()
    lead = Contestant.query.filter_by(contestant_id=couple.lead_id).first().get_full_name()
    follow = Contestant.query.filter_by(contestant_id=couple.follow_id).first().get_full_name()
    db.session.delete(couple)
    db.session.commit()
    flash(f'{lead} and {follow} are no longer dancing {POLKA} together.', 'alert-info')
    return redirect(url_for('blind_date_assistant.create_couple_polka'))