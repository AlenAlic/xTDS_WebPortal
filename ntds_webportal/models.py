from ntds_webportal import db, login, Anonymous
from flask import current_app, url_for, redirect, render_template, g, flash
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ntds_webportal.data import ACCESS, PROFILE_ACCESS, MESSAGES_ACCESS
from ntds_webportal.email import send_email
from ntds_webportal.values import *
from functools import wraps
from time import time
from datetime import datetime as dt
import datetime
import jwt
from ntds_webportal.base_functions import str2bool
from sqlalchemy import or_
import enum
import random
from random import shuffle
import itertools
from adjudication_system.skating import SkatingDance, SkatingSummary, CompetitionResult


USERS = 'users'
TEAMS = 'teams'
TEAM_FINANCES = 'team_finances'
TOURNAMENT_STATE = 'tournament_state'
SYSTEM_CONFIGURATION = 'system_configuration'
RAFFLE_CONFIGURATION = 'raffle_configuration'
NOTIFICATIONS = 'notifications'
ATTENDED_PREVIOUS_TOURNAMENT_CONTESTANT = 'attended_previous_tournament_contestant'
NOT_SELECTED_CONTESTANT = 'not_selected_contestant'
EXCLUDED_FROM_CLEARING = [USERS, TEAMS, TEAM_FINANCES, TOURNAMENT_STATE, SYSTEM_CONFIGURATION, RAFFLE_CONFIGURATION,
                          ATTENDED_PREVIOUS_TOURNAMENT_CONTESTANT, NOT_SELECTED_CONTESTANT]


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def requires_access_level(access_levels):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.access not in access_levels:
                flash("Page inaccessible.")
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def requires_adjudicator_access_level(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_adjudicator():
            flash("Page inaccessible.")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def requires_tournament_state(state):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.ts.state() >= state:
                flash("Page currently inaccessible.")
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def requires_testing_environment(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('ENV') not in TESTING_ENVIRONMENTS:
            flash("Cannot access this page in production.", "alert-warning")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# noinspection PyUnresolvedReferences
class User(UserMixin, Anonymous, db.Model):
    __tablename__ = USERS
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    access = db.Column(db.Integer, index=True, nullable=False)
    is_active = db.Column(db.Boolean, index=True, nullable=False, default=False)
    send_new_messages_email = db.Column(db.Boolean, nullable=False, default=True)
    activate = db.Column(db.Boolean, nullable=False, default=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    team = db.relationship('Team')
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'))
    dancer = db.relationship('Contestant', backref=db.backref("user", uselist=False), single_parent=True,
                             cascade='all, delete-orphan')
    volunteer_id = db.Column(db.Integer, db.ForeignKey('super_volunteer.volunteer_id'))
    super_volunteer = db.relationship('SuperVolunteer', backref=db.backref("user", uselist=False), single_parent=True,
                                      cascade='all, delete-orphan')
    adjudicator_id = db.Column(db.Integer, db.ForeignKey('adjudicator.adjudicator_id'))
    adjudicator = db.relationship('Adjudicator', backref=db.backref("user", uselist=False), single_parent=True,
                                  cascade='all, delete-orphan')

    def __repr__(self):
        if self.is_dancer():
            return f'{self.dancer}'
        if self.is_super_volunteer():
            return f'{self.super_volunteer}'
        return f'{self.username}'

    def get_id(self):
        return self.user_id

    def is_admin(self):
        return self.access == ACCESS[ADMIN]

    def is_organizer(self):
        return self.access == ACCESS[ORGANIZER]

    def is_tc(self):
        return self.access == ACCESS[TEAM_CAPTAIN]

    def is_treasurer(self):
        return self.access == ACCESS[TREASURER]

    def is_bda(self):
        return self.access == ACCESS[BLIND_DATE_ASSISTANT]

    def is_cia(self):
        return self.access == ACCESS[CHECK_IN_ASSISTANT]

    def is_ada(self):
        return self.access == ACCESS[ADJUDICATOR_ASSISTANT]

    def is_dancer(self):
        return self.access == ACCESS[DANCER]

    def is_super_volunteer(self):
        return self.access == ACCESS[SUPER_VOLUNTEER]

    def is_tournament_office_manager(self):
        return self.access == ACCESS[TOURNAMENT_OFFICE_MANAGER]

    def is_floor_manager(self):
        return self.access == ACCESS[FLOOR_MANAGER]

    def is_adjudicator(self):
        return self.adjudicator is not None

    def allowed(self, access_level):
        return self.access == access_level

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        # noinspection PyUnresolvedReferences
        return jwt.encode({'reset_password': self.user_id, 'exp': time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def unread_notifications(self):
        return Notification.query.filter_by(user=self, unread=True).count()

    @staticmethod
    def open_partner_requests():
        return len([r for r in PartnerRequest.query.filter_by(state=PartnerRequest.STATE['Open']).all() if
                    r.other.contestant_info.team == current_user.team])

    def open_name_change_requests(self):
        if self.is_organizer():
            return NameChangeRequest.open_requests()
        return 0

    # noinspection PyUnresolvedReferences
    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except jwt.exceptions.InvalidTokenError:
            return 'error'
        return User.query.get(user_id)

    def team_captains_selected(self):
        if self.has_dancers_registered():
            return g.sc.number_of_teamcaptains - \
                   len(db.session.query(ContestantInfo).filter(ContestantInfo.team == current_user.team,
                                                               ContestantInfo.team_captain.is_(True)).all())
        else:
            return 0

    def has_dancers_registered(self):
        count = 0
        if self.is_tc():
            count += Contestant.query.join(StatusInfo, ContestantInfo) \
                .filter(ContestantInfo.team == current_user.team).count()
        return count > 0

    def number_of_dancers_with_status(self, status):
        count = 0
        if self.is_tc():
            count += Contestant.query.join(StatusInfo, ContestantInfo) \
                .filter(ContestantInfo.team == current_user.team, StatusInfo.status == status).count()
        return count

    def registered_dancers(self):
        return self.number_of_dancers_with_status(REGISTERED) + self.number_of_dancers_with_status(NO_GDPR)

    def selected_dancers(self):
        return self.number_of_dancers_with_status(SELECTED)

    def dancers_with_feedback(self):
        count = 0
        if self.is_tc():
            count += Contestant.query.join(StatusInfo, ContestantInfo) \
                .filter(ContestantInfo.team == current_user.team, StatusInfo.status != CANCELLED,
                        StatusInfo.feedback_about_information != "").count()
        return count

    def has_profile_access(self):
        return self.access in PROFILE_ACCESS

    def has_messages_access(self):
        return self.access in MESSAGES_ACCESS


class Team(db.Model):
    __tablename__ = TEAMS
    team_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(128), nullable=False)
    city = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False, unique=True)
    amount_paid = db.Column(db.Integer, nullable=False, default=0)
    contestants = db.relationship('ContestantInfo', back_populates="team")

    def __repr__(self):
        if g.sc.tournament == NTDS:
            return '{}'.format(self.name)
        else:
            return '{}'.format(self.city)

    def is_active(self):
        team_captain = User.query.filter(User.access == ACCESS[TEAM_CAPTAIN], User.team_id == self.team_id).first()
        return team_captain.is_active is True

    def confirmed_dancers(self):
        return Contestant.query.join(ContestantInfo, StatusInfo)\
            .filter(ContestantInfo.team == self, StatusInfo.status == CONFIRMED).order_by(Contestant.first_name).all()

    def cancelled_dancers_with_merchandise(self):
        dancers = Contestant.query.join(ContestantInfo, StatusInfo)\
            .filter(ContestantInfo.team == self, StatusInfo.status == CANCELLED).order_by(Contestant.first_name).all()
        return [d for d in dancers if d.merchandise_info.ordered_merchandise()]

    def guaranteed_dancers(self):
        return Contestant.query.join(ContestantInfo, StatusInfo)\
            .filter(ContestantInfo.team == self, StatusInfo.status == REGISTERED,
                    or_(ContestantInfo.team_captain.is_(True), StatusInfo.guaranteed_entry.is_(True)))\
            .order_by(Contestant.first_name).all()


class Contestant(db.Model):
    __tablename__ = 'contestants'
    contestant_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    prefixes = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    contestant_info = db.relationship('ContestantInfo', back_populates='contestant', uselist=False,
                                      cascade='all, delete-orphan')
    dancing_info = db.relationship('DancingInfo', back_populates='contestant', cascade='all, delete-orphan')
    volunteer_info = db.relationship('VolunteerInfo', back_populates='contestant', uselist=False,
                                     cascade='all, delete-orphan')
    additional_info = db.relationship('AdditionalInfo', back_populates='contestant', uselist=False,
                                      cascade='all, delete-orphan')
    status_info = db.relationship('StatusInfo', back_populates='contestant', uselist=False,
                                  cascade='all, delete-orphan')
    payment_info = db.relationship('PaymentInfo', back_populates='contestant', uselist=False,
                                   cascade='all, delete-orphan')
    merchandise_info = db.relationship('MerchandiseInfo', back_populates='contestant', uselist=False,
                                       cascade='all, delete-orphan')
    dancers = db.relationship('Dancer', back_populates='contestant', cascade='all, delete-orphan')

    def __repr__(self):
        return f'{self.get_full_name()}'

    def get_full_name(self):
        if self.prefixes is None or self.prefixes == '':
            return ' '.join((self.first_name, self.last_name))
        else:
            return ' '.join((self.first_name, self.prefixes, self.last_name))

    def get_last_name(self):
        if self.prefixes is None or self.prefixes == '':
            return self.last_name
        else:
            return ' '.join((self.prefixes, self.last_name))

    def capitalize_name(self):
        self.first_name.title()
        self.last_name.title()

    def competition(self, competition):
        return [di for di in self.dancing_info if di.competition == competition][0]

    def cancel_registration(self):
        self.status_info.set_status(CANCELLED)
        for di in self.dancing_info:
            di.set_partner(None)
        self.contestant_info.team_captain = False
        self.additional_info.bus_to_brno = False
        if self.status_info.payment_required:
            if int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()) < \
                    g.sc.finances_refund_date:
                if g.sc.finances_full_refund:
                    self.payment_info.full_refund = True
                if g.sc.finances_partial_refund:
                    self.payment_info.partial_refund = True
        if int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()) < \
                g.sc.merchandise_closing_date:
            self.merchandise_info.cancel_merchandise()
        db.session.commit()

    def deletable(self):
        return not (self.status_info.payment_required or self.merchandise_info.ordered_merchandise() or
                    self.payment_info.entry_paid or self.payment_info.full_refund or self.payment_info.partial_refund)

    def get_dancing_info(self, competition):
        for di in self.dancing_info:
            if di.competition == competition:
                return di
        return None

    def dancing_information(self, competition):
        for di in self.dancing_info:
            if di.competition == competition:
                return di

    def is_dancing(self):
        return len(set([di.level for di in self.dancing_info if di.level != NO])) > 0

    def role(self):
        roles = sorted(list(set([di.role for di in self.dancing_info if di.role != NO])))
        if len(roles) == 1:
            return roles[0]
        else:
            return BOTH

    def to_dict(self):
        data = {
            'contestant_id': self.contestant_id,
            # 'first_name':  self.first_name,
            # 'last_name': self.get_last_name(),
            'full_name': self.get_full_name(),
            # 'email': self.email,
            'contestant_info': self.contestant_info.to_dict(),
            # 'dancing_info': {},
            # 'volunteer_info': self.volunteer_info.to_dict(),
            # 'additional_info': self.additional_info.to_dict(),
            'status_info': self.status_info.to_dict(),
            'merchandise_info': self.merchandise_info.to_dict(),
            'payment_info': self.payment_info.to_dict(),
        }
        # dis = [di.to_dict() for di in self.dancing_info]
        # for di in dis:
        #     for key, val in di.items():
        #         data['dancing_info'][key] = val
        return data


class ContestantInfo(db.Model):
    __tablename__ = 'contestant_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='contestant_info')
    number = db.Column(db.Integer, nullable=False)
    team_captain = db.Column(db.Boolean, nullable=False, default=False)
    student = db.Column(db.String(128), index=True, nullable=False, default=STUDENT)
    first_time = db.Column(db.Boolean, index=True, nullable=False, default=False)
    diet_allergies = db.Column('Diet/Allergies', db.String(512), nullable=True, default="")
    organization_diet_notes = db.Column('Diet/Allergies Notes', db.String(512), nullable=False, default="")
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)
    team = db.relationship('Team', back_populates="contestants")

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def team_name(self):
        if g.sc.tournament == g.data.NTDS:
            return f"{self.team.name} ({self.team.city})"

    def to_dict(self):
        data = {
            'number': self.number,
            'team_captain':  self.team_captain,
            'student': self.student,
            'first_time': self.first_time,
            'diet_allergies': self.diet_allergies,
            'team': self.team.name,
        }
        return data


class DancingInfo(db.Model):
    __tablename__ = 'dancing_info'
    __table_args__ = (db.UniqueConstraint('contestant_id', 'competition', 'level'),)
    contest_id = db.Column(db.Integer, primary_key=True)
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'))
    contestant = db.relationship('Contestant', foreign_keys=contestant_id)
    competition = db.Column(db.String(128), nullable=False)
    level = db.Column(db.String(128), nullable=False, default=NO)
    role = db.Column(db.String(128), nullable=False, default=NO)
    blind_date = db.Column(db.Boolean, nullable=False, default=False)
    partner = db.Column(db.Integer, nullable=True, default=None)

    def __repr__(self):
        return '{competition}: {name}'.format(competition=self.competition, name=self.contestant)

    def valid_match(self, other, breitensport=True):
        errors = []
        if breitensport and (self.blind_date or other.blind_date):
            errors.append("At least one of the dancers must blind date.")
        else:
            if self.competition != other.competition:
                errors.append("The dancers are not in the same competition.")
            if self.level != other.level:
                errors.append("The dancers are not in the same level.")
            if self.role == other.role:
                errors.append("The dancers are not a valid Lead/Follow pair.")
            if self.partner is not None:
                errors.append(f"{self.contestant.get_full_name()} already has a partner.")
            if other.partner is not None:
                errors.append(f"{other.contestant.get_full_name()} already has a partner.")
        return not errors, errors

    def set_partner(self, contestant_id):
        other_dancer = DancingInfo.query.filter(DancingInfo.competition == self.competition,
                                                DancingInfo.partner == self.contestant_id).first()
        if other_dancer is not None:
            other_dancer.partner = None

        if contestant_id is None:
            self.partner = None
        else:
            other_dancer = DancingInfo.query.filter(DancingInfo.competition == self.competition,
                                                    DancingInfo.contestant_id == contestant_id).first()
            if other_dancer is not None:
                self.partner = other_dancer.contestant_id
                other_dancer.partner = self.contestant_id
        db.session.commit()

    def not_dancing(self, competition):
        self.competition = competition
        self.level = NO
        self.role = NO
        self.blind_date = False
        self.partner = None

    def to_dict(self):
        data = {
            self.competition: {
                'level':  self.level,
                'role': self.role,
                'blind_date': self.blind_date,
                'partner': self.partner,
            }
        }
        return data


class VolunteerInfo(db.Model):
    __tablename__ = 'volunteer_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='volunteer_info')
    volunteer = db.Column(db.String(16), nullable=False, default=NO)
    first_aid = db.Column(db.String(16), nullable=False, default=NO)
    emergency_response_officer = db.Column(db.String(16), nullable=False, default=NO)
    jury_ballroom = db.Column(db.String(16), nullable=False, default=NO)
    jury_latin = db.Column(db.String(16), nullable=False, default=NO)
    level_ballroom = db.Column(db.String(16), nullable=False, default=BELOW_D)
    level_latin = db.Column(db.String(16), nullable=False, default=BELOW_D)
    license_jury_ballroom = db.Column(db.String(16), nullable=False, default=NO)
    license_jury_latin = db.Column(db.String(16), nullable=False, default=NO)
    jury_salsa = db.Column(db.String(16), nullable=False, default=NO)
    jury_polka = db.Column(db.String(16), nullable=False, default=NO)
    selected_adjudicator = db.Column(db.Boolean, nullable=False, default=False)
    adjudicator_notes = db.Column(db.String(512), nullable=False, default="")

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def not_volunteering(self):
        self.volunteer = NO
        self.first_aid = NO
        self.emergency_response_officer = NO
        self.jury_ballroom = NO
        self.jury_latin = NO
        self.license_jury_ballroom = NO
        self.license_jury_latin = NO
        self.level_ballroom = BELOW_D
        self.level_latin = BELOW_D
        self.jury_salsa = NO
        self.jury_polka = NO

    def volunteering(self):
        return self.volunteer != NO or self.first_aid != NO or self.emergency_response_officer != NO

    def adjudicating(self):
        return self.jury_ballroom != NO or self.jury_latin != NO or self.jury_salsa != NO or self.jury_polka != NO

    def to_dict(self):
        data = {
            'volunteer': self.volunteer,
            'first_aid':  self.first_aid,
            'emergency_response_officer': self.emergency_response_officer,
            'jury_ballroom': self.jury_ballroom,
            'jury_latin': self.jury_latin,
            'level_ballroom': self.level_ballroom,
            'level_latin': self.level_latin,
            'license_jury_ballroom': self.license_jury_ballroom,
            'license_jury_latin': self.license_jury_latin,
            'jury_salsa': self.jury_salsa,
            'jury_polka': self.jury_polka,
        }
        return data


class AdditionalInfo(db.Model):
    __tablename__ = 'additional_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='additional_info')
    sleeping_arrangements = db.Column(db.Boolean, nullable=False, default=False)
    bus_to_brno = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def to_dict(self):
        data = {
            'sleeping_arrangements': self.sleeping_arrangements,
            'bus_to_tournament':  self.bus_to_brno,
        }
        return data


class StatusInfo(db.Model):
    __tablename__ = 'status_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='status_info')
    status = db.Column(db.String(16), index=True, default=REGISTERED)
    payment_required = db.Column(db.Boolean, index=True, nullable=False, default=False)
    raffle_status = db.Column(db.String(16), index=True, default=REGISTERED)
    guaranteed_entry = db.Column(db.Boolean, nullable=False, default=False)
    checked_in = db.Column(db.Boolean, nullable=False, default=False)
    received_starting_number = db.Column(db.Boolean, nullable=False, default=False)
    feedback_about_information = db.Column(db.String(512), nullable=True, default=None)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def set_status(self, status):
        if status is not None:
            self.status = status
            self.raffle_status = status
        if self.status == CONFIRMED:
            self.payment_required = True
        elif self.status == REGISTERED:
            self.payment_required = False

    def dancing_lead(self):
        roles = [d.role for d in self.contestant.dancing_info]
        return LEAD in roles

    def remove_payment_requirement(self):
        self.payment_required = False
        self.contestant.payment_info.remove_refund()
        db.session.commit()

    def to_dict(self):
        data = {
            # 'status': self.status,
            # 'payment_required':  self.payment_required,
            # 'raffle_status': self.raffle_status,
            'dancing_lead': self.dancing_lead(),
            'guaranteed_entry': self.guaranteed_entry,
            'checked_in': self.checked_in,
            'received_starting_number': self.received_starting_number,
            # 'feedback_about_information': self.feedback_about_information,
        }
        return data


class PaymentInfo(db.Model):
    __tablename__ = 'payment_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='payment_info')
    entry_paid = db.Column(db.Boolean, index=True, nullable=False, default=False)
    full_refund = db.Column(db.Boolean, index=True, nullable=False, default=False)
    partial_refund = db.Column(db.Boolean, index=True, nullable=False, default=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def has_refund(self):
        return self.full_refund is True or self.partial_refund is True

    def all_paid(self, set_paid=None):
        if set_paid is not None:
            if set_paid:
                return self.set_all_paid()
            elif not set_paid:
                return self.set_all_unpaid()
        else:
            m_info = MerchandiseInfo.query.filter(MerchandiseInfo.contestant_id == self.contestant_id).first()
            if m_info.ordered_merchandise():
                return m_info.merchandise_paid() and self.entry_paid
            else:
                return self.entry_paid

    def merchandise_paid(self, set_paid=None):
        m_info = MerchandiseInfo.query.filter(MerchandiseInfo.contestant_id == self.contestant_id).first()
        if set_paid is not None:
            if set_paid:
                return m_info.set_merchandise_paid()
            elif not set_paid:
                return m_info.set_merchandise_unpaid()
        else:
            return m_info.merchandise_paid()

    def set_all_paid(self):
        m_info = MerchandiseInfo.query.filter(MerchandiseInfo.contestant_id == self.contestant_id).first()
        if m_info.ordered_merchandise():
            m_info.set_merchandise_paid()
        self.entry_paid = True
        db.session.commit()
        return True

    def partially_paid(self):
        m_info = MerchandiseInfo.query.filter(MerchandiseInfo.contestant_id == self.contestant_id).first()
        if m_info.ordered_merchandise():
            return m_info.merchandise_paid() or self.entry_paid
        else:
            return self.entry_paid

    def set_all_unpaid(self):
        m_info = MerchandiseInfo.query.filter(MerchandiseInfo.contestant_id == self.contestant_id).first()
        if m_info.ordered_merchandise():
            m_info.set_merchandise_unpaid()
        self.entry_paid = False
        db.session.commit()
        return False

    def remove_refund(self):
        self.partial_refund = False
        self.full_refund = False
        db.session.commit()

    def to_dict(self):
        data = {
            'entry_paid': self.entry_paid,
            # 'full_refund': self.full_refund,
            # 'partial_refund': self.partial_refund,
            'all_paid': self.all_paid(),
            'merchandise_paid': self.merchandise_paid(),
        }
        return data


class MerchandiseInfo(db.Model):
    __tablename__ = 'merchandise_info'
    order_id = db.Column(db.Integer, primary_key=True)
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'))
    contestant = db.relationship('Contestant', back_populates='merchandise_info')
    t_shirt = db.Column(db.String(128), nullable=False, default=NO)
    mug = db.Column(db.Boolean, nullable=False, default=False)
    bag = db.Column(db.Boolean, nullable=False, default=False)
    t_shirt_paid = db.Column(db.Boolean, index=True, nullable=False, default=False)
    mug_paid = db.Column(db.Boolean, index=True, nullable=False, default=False)
    bag_paid = db.Column(db.Boolean, index=True, nullable=False, default=False)
    merchandise_received = db.Column(db.Boolean, index=True, nullable=False, default=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def ordered_merchandise(self):
        return self.t_shirt != NO or self.mug or self.bag

    def merchandise_paid(self):
        t_shirt_paid = self.t_shirt_paid
        mug_paid = self.mug_paid
        bag_paid = self.bag_paid
        if self.t_shirt == NO:
            t_shirt_paid = True
        if not self.mug:
            mug_paid = True
        if not self.bag:
            bag_paid = True
        return t_shirt_paid and mug_paid and bag_paid

    def set_merchandise_paid(self):
        if self.ordered_merchandise():
            if g.sc.t_shirt_sold and self.t_shirt != NO:
                self.t_shirt_paid = True
            if g.sc.mug_sold and self.mug:
                self.mug_paid = True
            if g.sc.bag_sold and self.bag:
                self.bag_paid = True
            db.session.commit()

    def set_merchandise_unpaid(self):
        if self.ordered_merchandise():
            if g.sc.t_shirt_sold and self.t_shirt:
                self.t_shirt_paid = False
            if g.sc.mug_sold and self.mug:
                self.mug_paid = False
            if g.sc.bag_sold and self.bag:
                self.bag_paid = False
            db.session.commit()

    def merchandise_price(self):
        total_price = 0
        if self.ordered_merchandise():
            if self.t_shirt != NO:
                total_price += g.sc.t_shirt_price
            if self.mug:
                total_price += g.sc.mug_price
            if self.bag:
                total_price += g.sc.bag_price
        return total_price

    def cancel_merchandise(self):
        self.t_shirt = NO
        self.mug = False
        self.bag = False
        db.session.commit()

    def to_dict(self):
        data = {
            't_shirt': self.t_shirt,
            'mug':  self.mug,
            'bag': self.bag,
            't_shirt_paid': self.t_shirt_paid,
            'mug_paid': self.mug_paid,
            'bag_paid': self.bag_paid,
            'merchandise_received': self.merchandise_received,
            'ordered_merchandise': self.ordered_merchandise(),
        }
        return data


class AttendedPreviousTournamentContestant(db.Model):
    __tablename__ = ATTENDED_PREVIOUS_TOURNAMENT_CONTESTANT
    contestant_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    prefixes = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    tournaments = db.Column(db.String(8192), nullable=False)

    def set_tournaments(self, new_tournament):
        if self.tournaments is not None:
            old_tournaments = self.tournaments.split(",")
            if new_tournament not in old_tournaments:
                old_tournaments.append(new_tournament)
                self.tournaments = ",".join(old_tournaments)
        else:
            self.tournaments = new_tournament
        db.session.commit()


class NotSelectedContestant(db.Model):
    __tablename__ = NOT_SELECTED_CONTESTANT
    contestant_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    prefixes = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    tournament = db.Column(db.String(16), nullable=False)


def send_new_messages_email(sender, recipient):
    send_email('New message - xTDS WebPortal',
               recipients=[recipient.email],
               text_body=render_template('email/new_message.txt', sender=sender, recipient=recipient),
               html_body=render_template('email/new_message.html', sender=sender, recipient=recipient))


def send_new_automated_message_email(recipient):
    send_email('New automated message - xTDS WebPortal',
               recipients=[recipient.email],
               text_body=render_template('email/new_automated_message.txt', recipient=recipient),
               html_body=render_template('email/new_automated_message.html', recipient=recipient))


class Notification(db.Model):
    __tablename__ = NOTIFICATIONS
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    unread = db.Column(db.Boolean, index=True, default=True)
    archived = db.Column(db.Boolean, index=True, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=dt.utcnow)
    title = db.Column(db.String(128))
    text = db.Column(db.Text())
    destination = db.Column(db.String(256))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('notifications', lazy=True))
    sender = db.relationship('User', foreign_keys=[sender_id])

    def __repr__(self):
        return 'message to: {} \ntitle: {} \nlink: {}\n'.format(self.user.username, self.title, self.destination,
                                                                self.text)

    def get_sender(self):
        if not self.sender:
            return 'xTDS - automated message'
        else:
            return self.sender

    def get_sender_email(self):
        if not self.sender:
            return 'xTDS system'
        else:
            return self.sender

    def send(self):
        if dt.utcnow().timestamp() < g.sc.tournament_starting_date:
            if self.user.send_new_messages_email:
                if self.sender is not None:
                    send_new_messages_email(sender=self.sender, recipient=self.user)
                else:
                    send_new_automated_message_email(recipient=self.user)
        db.session.add(self)
        db.session.commit()


class PartnerRequest(db.Model):
    STATE = {'Open': 1, 'Accepted': 2, 'Rejected': 3, 'Cancelled': 4}
    STATE_NAMES = {v: k for k, v in STATE.items()}

    __tablename__ = 'partner_request'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=dt.utcnow)
    remark = db.Column(db.Text())
    response = db.Column(db.Text())
    level = db.Column(db.String(128), nullable=False, default=NO)
    competition = db.Column(db.String(128), nullable=False, default=BREITENSPORT)
    dancer_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'))
    other_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'))
    state = db.Column(db.Integer, default=STATE['Open'])
    dancer = db.relationship('Contestant', foreign_keys=[dancer_id])
    other = db.relationship('Contestant', foreign_keys=[other_id])

    def accept(self):
        self.state = self.STATE['Accepted']
        self.dancer.competition(self.competition).set_partner(self.other_id)
        self.notify()

    def reject(self):
        self.state = self.STATE['Rejected']
        self.notify()

    def cancel(self):
        self.state = self.STATE['Cancelled']
        db.session.commit()

    def notify(self):
        recipients = User.query.filter_by(team=self.dancer.contestant_info.team, access=ACCESS[TEAM_CAPTAIN])
        for u in recipients:
            n = Notification()
            n.title = f"{self.state_name()} - Partner request: {self.dancer.get_full_name()} with " \
                      f"{self.other.get_full_name()} in {self.competition}"
            n.user = u
            n.text = render_template('notifications/partner_request.html', request=self)
            n.send()

    def state_name(self):
        return self.STATE_NAMES[self.state]


class NameChangeRequest(db.Model):
    STATE = {'Open': 1, 'Accepted': 2, 'Rejected': 3}
    STATE_NAMES = {v: k for k, v in STATE.items()}

    __tablename__ = 'name_change_requests'
    id = db.Column(db.Integer, primary_key=True)
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'))
    contestant = db.relationship('Contestant', foreign_keys=[contestant_id])
    first_name = db.Column(db.String(128), nullable=False)
    prefixes = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=False)
    state = db.Column(db.Integer, default=STATE['Open'])
    response = db.Column(db.Text())

    def accept(self):
        self.state = self.STATE['Accepted']
        self.notify()
        self.contestant.first_name = self.first_name
        self.contestant.last_name = self.last_name
        self.contestant.prefixes = self.prefixes

    def reject(self):
        self.state = self.STATE['Rejected']
        self.notify()

    def notify(self):
        recipients = User.query.filter_by(team=self.contestant.contestant_info.team, access=ACCESS[TEAM_CAPTAIN])
        for u in recipients:
            n = Notification()
            n.title = f"{self.state_name()} - Name change request: " \
                      f"{self.contestant.get_full_name()} to {self.get_full_name()}"
            n.user = u
            n.text = render_template('notifications/name_change_request.html', request=self)
            n.send()

    def get_full_name(self):
        if self.prefixes is None or self.prefixes == '':
            return ' '.join((self.first_name, self.last_name))
        else:
            return ' '.join((self.first_name, self.prefixes, self.last_name))

    def state_name(self):
        return self.STATE_NAMES[self.state]

    @staticmethod
    def open_requests():
        return NameChangeRequest.query.filter_by(state=NameChangeRequest.STATE['Open']).count()


class TournamentState(db.Model):
    __tablename__ = TOURNAMENT_STATE
    lock = db.Column(db.Integer, primary_key=True)
    organizer_account_set = db.Column(db.Boolean, nullable=False, default=False)
    system_configured = db.Column(db.Boolean, nullable=False, default=False)
    website_accessible_to_teamcaptains = db.Column(db.Boolean, nullable=False, default=False)
    registration_period_started = db.Column(db.Boolean, nullable=False, default=False)
    registration_open = db.Column(db.Boolean, nullable=False, default=False)
    raffle_system_configured = db.Column(db.Boolean, nullable=False, default=False)
    main_raffle_taken_place = db.Column(db.Boolean, nullable=False, default=False)
    main_raffle_result_visible = db.Column(db.Boolean, nullable=False, default=False)
    numbers_rearranged = db.Column(db.Boolean, nullable=False, default=False)
    raffle_completed_message_sent = db.Column(db.Boolean, nullable=False, default=False)
    merchandise_finalized = db.Column(db.Boolean, nullable=False, default=False)
    super_volunteer_registration_open = db.Column(db.Boolean, nullable=False, default=False)
    dancers_imported = db.Column(db.Boolean, nullable=False, default=False)
    couples_imported = db.Column(db.Boolean, nullable=False, default=False)

    def state(self):
        if self.main_raffle_result_visible:
            return RAFFLE_CONFIRMED
        if self.main_raffle_taken_place:
            return RAFFLE_COMPLETED
        if self.registration_open:
            return REGISTRATION_OPEN
        if self.registration_period_started and not self.registration_open:
            return REGISTRATION_CLOSED
        if self.registration_period_started:
            return REGISTRATION_STARTED
        if self.website_accessible_to_teamcaptains:
            return TEAM_CAPTAINS_HAVE_ACCESS
        if self.system_configured:
            return SYSTEM_CONFIGURED
        if self.organizer_account_set:
            return ORGANIZERS_NOTIFIED
        return 0

    # def state_flash_message(self):
    #     if not self.system_configured:
    #         return WEBSITE_NOT_CONFIGURED_TEXT
    #     if not self.website_accessible_to_teamcaptains:
    #         return TEAM_CAPTAINS_DO_NOT_HAVE_ACCESS_TEXT
    #     if not self.registration_period_started:
    #         return REGISTRATION_NOT_STARTED_TEXT
    #     if self.registration_period_started and not self.registration_open:
    #         return REGISTRATION_NOT_OPEN_TEXT
    #     if not self.main_raffle_result_visible:
    #         return RAFFLE_NOT_CONFIRMED_TEXT


class SalsaPartners(db.Model):
    __tablename__ = 'salsa_partners'
    couple_id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, nullable=False)
    follow_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return 'Lead: {} - Follow {}'.format(self.lead_id, self.follow_id)


class PolkaPartners(db.Model):
    __tablename__ = 'polka_partners'
    couple_id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, nullable=False)
    follow_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return 'Lead: {} - Follow {}'.format(self.lead_id, self.follow_id)


class SystemConfiguration(db.Model):
    __tablename__ = SYSTEM_CONFIGURATION
    id = db.Column(db.Integer, primary_key=True)

    website_accessible = db.Column(db.Boolean, nullable=False, default=True)

    system_configuration_accessible = db.Column(db.Boolean, nullable=False, default=False)
    tournament = db.Column(db.String(4), nullable=False, default=NTDS)
    year = db.Column(db.Integer, nullable=False, default=2018)
    city = db.Column(db.String(128), nullable=False, default=ENSCHEDE)
    tournament_starting_date = db.Column(db.Integer, nullable=False, default=1538449200)

    number_of_teamcaptains = db.Column(db.Integer, nullable=False, default=1)

    beginners_level = db.Column(db.Boolean, nullable=False, default=True)
    closed_level = db.Column(db.Boolean, nullable=False, default=True)
    breitensport_obliged_blind_date = db.Column(db.Boolean, nullable=False, default=True)
    salsa_competition = db.Column(db.Boolean, nullable=False, default=False)
    polka_competition = db.Column(db.Boolean, nullable=False, default=False)

    student_price = db.Column(db.Integer, nullable=False, default=DEFAULT_STUDENT_PRICE)
    non_student_price = db.Column(db.Integer, nullable=False, default=DEFAULT_NON_STUDENT_PRICE)
    phd_student_category = db.Column(db.Boolean, nullable=False, default=False)
    phd_student_price = db.Column(db.Integer, nullable=False, default=DEFAULT_PHD_STUDENT_PRICE)

    first_time_ask = db.Column(db.Boolean, nullable=False, default=True)
    ask_diet_allergies = db.Column(db.Boolean, nullable=False, default=True)
    ask_volunteer = db.Column(db.Boolean, nullable=False, default=True)
    ask_first_aid = db.Column(db.Boolean, nullable=False, default=True)
    ask_emergency_response_officer = db.Column(db.Boolean, nullable=False, default=True)
    ask_adjudicator_highest_achieved_level = db.Column(db.Boolean, nullable=False, default=True)
    ask_adjudicator_certification = db.Column(db.Boolean, nullable=False, default=True)

    t_shirt_sold = db.Column(db.Boolean, nullable=False, default=True)
    t_shirt_price = db.Column(db.Integer, nullable=False, default=0)
    mug_sold = db.Column(db.Boolean, nullable=False, default=True)
    mug_price = db.Column(db.Integer, nullable=False, default=0)
    bag_sold = db.Column(db.Boolean, nullable=False, default=True)
    bag_price = db.Column(db.Integer, nullable=False, default=0)
    merchandise_link = db.Column(db.String(1028), nullable=True)
    merchandise_closing_date = db.Column(db.Integer, nullable=False, default=1538449200)

    finances_full_refund = db.Column(db.Boolean, nullable=False, default=False)
    finances_partial_refund = db.Column(db.Boolean, nullable=False, default=True)
    finances_partial_refund_percentage = db.Column(db.Integer, nullable=False, default=70)
    finances_refund_date = db.Column(db.Integer, nullable=False, default=1538449200)

    main_page_link = db.Column(db.String(1028), nullable=True)
    terms_and_conditions_link = db.Column(db.String(1028), nullable=True)
    
    def get_participating_levels(self):
        participating_levels = []
        if self.beginners_level:
            participating_levels.append(BEGINNERS)
        participating_levels.append(BREITENSPORT)
        if self.closed_level:
            participating_levels.append(CLOSED)
        participating_levels.append(OPEN_CLASS)
        return participating_levels

    def get_participating_levels_including_not_dancing(self):
        participating_levels = self.get_participating_levels()
        participating_levels.append(NO)
        return participating_levels

    def check_in_accessible(self):
        return int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()) > \
                              self.tournament_starting_date

    def merchandise(self):
        return self.t_shirt_sold or self.mug_sold or self.bag_sold

    @staticmethod
    def merchandise_name(number):
        order = {0: 'T-shirt', 1: 'Mug', 2: 'Bag'}
        return order[number]

    def merchandise_sold(self, number):
        order = {0: self.t_shirt_sold, 1: self.mug_sold, 2: self.bag_sold}
        return order[number]

    def number_of_merchandise(self, exclude_t_shirt=False):
        counter = 0
        if self.t_shirt_sold and not exclude_t_shirt:
            counter += 1
        if self.mug_sold:
            counter += 1
        if self.bag_sold:
            counter += 1
        return counter


class RaffleConfiguration(db.Model):
    __tablename__ = RAFFLE_CONFIGURATION
    id = db.Column(db.Integer, primary_key=True)

    maximum_number_of_dancers = db.Column(db.Integer, nullable=False, default=400)
    selection_buffer = db.Column(db.Integer, nullable=False, default=40)

    beginners_guaranteed_entry_cutoff = db.Column(db.Boolean, nullable=False, default=False)
    beginners_guaranteed_cutoff = db.Column(db.Integer, nullable=False, default=0)
    beginners_guaranteed_per_team = db.Column(db.Boolean, nullable=False, default=False)
    beginners_minimum_entry_per_team = db.Column(db.Integer, nullable=False, default=0)
    beginners_increased_chance = db.Column(db.Boolean, nullable=False, default=False)

    first_time_guaranteed_entry = db.Column(db.Boolean, nullable=False, default=False)
    first_time_increased_chance = db.Column(db.Boolean, nullable=False, default=False)

    guaranteed_team_size = db.Column(db.Boolean, nullable=False, default=False)
    minimum_team_size = db.Column(db.Integer, nullable=False, default=0)

    lions_guaranteed_per_team = db.Column(db.Boolean, nullable=False, default=False)
    closed_lion = db.Column(db.Boolean, nullable=False, default=False)
    open_class_lion = db.Column(db.Boolean, nullable=False, default=False)
    lions_minimum_entry_per_team = db.Column(db.Integer, nullable=False, default=0)

    def get_lion_levels(self):
        lion_levels = [BEGINNERS, BREITENSPORT]
        if self.closed_lion:
            lion_levels.append(CLOSED)
        if self.open_class_lion:
            lion_levels.append(OPEN_CLASS)
        return lion_levels


class SuperVolunteer(db.Model):
    __tablename__ = 'super_volunteer'
    volunteer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    prefixes = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    diet_allergies = db.Column('Diet/Allergies', db.String(512), nullable=True, default="")
    organization_diet_notes = db.Column('Diet/Allergies Notes', db.String(512), nullable=True, default="")
    sleeping_arrangements = db.Column(db.Boolean, nullable=False, default=False)
    remark = db.Column(db.String(512), nullable=True, default=None)
    first_aid = db.Column(db.String(16), nullable=False, default=NO)
    emergency_response_officer = db.Column(db.String(16), nullable=False, default=NO)
    jury_ballroom = db.Column(db.String(16), nullable=False, default=NO)
    jury_latin = db.Column(db.String(16), nullable=False, default=NO)
    level_ballroom = db.Column(db.String(16), nullable=False, default=BELOW_D)
    level_latin = db.Column(db.String(16), nullable=False, default=BELOW_D)
    license_jury_ballroom = db.Column(db.String(16), nullable=False, default=NO)
    license_jury_latin = db.Column(db.String(16), nullable=False, default=NO)
    jury_salsa = db.Column(db.String(16), nullable=False, default=NO)
    jury_polka = db.Column(db.String(16), nullable=False, default=NO)
    selected_adjudicator = db.Column(db.Boolean, nullable=False, default=False)
    adjudicator_notes = db.Column(db.String(512), nullable=False, default="")

    def __repr__(self):
        return '{}'.format(self.get_full_name())

    def get_full_name(self):
        if self.prefixes is None or self.prefixes == '':
            return ' '.join((self.first_name, self.last_name))
        else:
            return ' '.join((self.first_name, self.prefixes, self.last_name))

    def get_last_name(self):
        if self.prefixes is None or self.prefixes == '':
            return self.last_name
        else:
            return ' '.join((self.prefixes, self.last_name))

    def capitalize_name(self):
        self.first_name.title()
        self.last_name.title()

    def volunteering(self):
        return self.first_aid != NO or self.emergency_response_officer != NO

    def adjudicating(self):
        return self.jury_ballroom != NO or self.jury_latin != NO or self.jury_salsa != NO or self.jury_polka != NO
    
    def update_data(self, form):
        self.first_name = form.first_name.data
        self.prefixes = form.prefixes.data if form.prefixes.data.replace(' ', '') != '' else None
        self.last_name = form.last_name.data
        self.capitalize_name()
        self.email = form.email.data
        self.sleeping_arrangements = str2bool(form.sleeping_arrangements.data)
        self.diet_allergies = form.diet_allergies.data
        self.first_aid = form.first_aid.data
        self.emergency_response_officer = form.emergency_response_officer.data
        self.jury_ballroom = form.jury_ballroom.data
        self.jury_latin = form.jury_latin.data
        self.license_jury_ballroom = form.license_jury_ballroom.data
        self.license_jury_latin = form.license_jury_latin.data
        self.level_ballroom = form.level_jury_ballroom.data
        self.level_latin = form.level_jury_latin.data
        self.jury_salsa = form.jury_salsa.data
        self.jury_polka = form.jury_polka.data
        self.remark = form.remark.data


TABLE_EVENT = 'event'
TABLE_COMPETITION = 'competition'
TABLE_DANCING_CLASS = 'dancing_class'
TABLE_DISCIPLINE = 'discipline'
TABLE_DANCE = 'dance'
TABLE_ADJUDICATOR = 'adjudicator'
TABLE_DANCER = 'dancer'
TABLE_COUPLE = 'couple'
TABLE_ROUND = 'round'
TABLE_DANCE_ACTIVE = 'dance_active'
TABLE_HEAT = 'heat'
TABLE_MARK = 'mark'
TABLE_FINAL_PLACING = 'final_placing'
TABLE_COUPLE_PRESENT = 'couple_present'
TABLE_ROUND_RESULT = 'round_result'

TABLE_COMPETITION_LEAD = 'competition_lead'
TABLE_COMPETITION_FOLLOW = 'competition_follow'
TABLE_COMPETITION_COUPLE = 'competition_couple'
TABLE_COMPETITION_ADJUDICATOR = 'competition_adjudicator'
TABLE_ROUND_DANCE = 'round_dance'
TABLE_ROUND_COUPLE = 'round_couple'
TABLE_HEAT_COUPLE = 'heat_couple'


ADJUDICATOR_SYSTEM_TABLES = [
    TABLE_EVENT,
    TABLE_COMPETITION,
    TABLE_DANCING_CLASS,
    TABLE_DISCIPLINE,
    TABLE_DANCE,
    # TABLE_ADJUDICATOR,
    TABLE_DANCER,
    TABLE_COUPLE,
    TABLE_ROUND,
    TABLE_DANCE_ACTIVE,
    TABLE_HEAT,
    TABLE_MARK,
    TABLE_FINAL_PLACING,
    TABLE_COUPLE_PRESENT,
    TABLE_ROUND_RESULT,
    TABLE_COMPETITION_LEAD,
    TABLE_COMPETITION_FOLLOW,
    TABLE_COMPETITION_COUPLE,
    TABLE_COMPETITION_ADJUDICATOR,
    TABLE_ROUND_DANCE,
    TABLE_ROUND_COUPLE,
    TABLE_HEAT_COUPLE,
]


class Event(db.Model):
    __tablename__ = TABLE_EVENT
    event_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    competitions = db.relationship('Competition', back_populates='event', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return '{}'.format(self.name)

    def has_competitions(self):
        return len(self.competitions) > 0

    def unique_dates(self):
        return list(sorted(set([c.when.date() for c in self.competitions])))

    def competitions_by_date(self):
        return list(sorted([c for c in self.competitions], key=lambda x: x.when))

    def competitions_on_day(self, date):
        return list(sorted([c for c in self.competitions if c.when.date() == date], key=lambda x: x.when))


competition_lead_table = db.Table(
    TABLE_COMPETITION_LEAD, db.Model.metadata,
    db.Column('competition_id', db.Integer,
              db.ForeignKey('competition.competition_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('dancer_id', db.Integer, db.ForeignKey('dancer.dancer_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.UniqueConstraint('competition_id', 'dancer_id', name='_competition_lead_uc')
)


competition_follow_table = db.Table(
    TABLE_COMPETITION_FOLLOW, db.Model.metadata,
    db.Column('competition_id', db.Integer,
              db.ForeignKey('competition.competition_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('dancer_id', db.Integer, db.ForeignKey('dancer.dancer_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.UniqueConstraint('competition_id', 'dancer_id', name='_competition_follow_uc')
)


competition_couple_table = db.Table(
    TABLE_COMPETITION_COUPLE, db.Model.metadata,
    db.Column('competition_id', db.Integer,
              db.ForeignKey('competition.competition_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('couple_id', db.Integer, db.ForeignKey('couple.couple_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.UniqueConstraint('competition_id', 'couple_id', name='_competition_couple_uc')
)


competition_adjudicator_table = db.Table(
    TABLE_COMPETITION_ADJUDICATOR, db.Model.metadata,
    db.Column('competition_id', db.Integer,
              db.ForeignKey('competition.competition_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('adjudicator_id', db.Integer,
              db.ForeignKey('adjudicator.adjudicator_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.UniqueConstraint('competition_id', 'adjudicator_id', name='_competition_adjudicator_uc')
)


class CompetitionMode(enum.Enum):
    single_partner = "Single partner"
    random_single_partner = "Random single partner"
    change_per_round = "Change partner per round"
    change_per_dance = "Change partner per dance"


class Competition(db.Model):
    __tablename__ = TABLE_COMPETITION
    competition_id = db.Column(db.Integer, primary_key=True)
    dancing_class_id = db.Column(db.Integer, db.ForeignKey('dancing_class.dancing_class_id',
                                                           onupdate="CASCADE", ondelete="CASCADE"))
    dancing_class = db.relationship("DancingClass", back_populates="competitions")
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.discipline_id',
                                                        onupdate="CASCADE", ondelete="CASCADE"))
    discipline = db.relationship("Discipline", back_populates="competitions")
    floors = db.Column(db.Integer, default=1)
    when = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    rounds = db.relationship("Round", back_populates="competition", cascade='all, delete, delete-orphan')
    mode = db.Column(db.Enum(CompetitionMode))
    couples = db.relationship("Couple", secondary=competition_couple_table, back_populates="competitions")
    leads = db.relationship("Dancer", secondary=competition_lead_table, back_populates="competitions_lead")
    follows = db.relationship("Dancer", secondary=competition_follow_table, back_populates="competitions_follow")
    adjudicators = db.relationship("Adjudicator", secondary=competition_adjudicator_table)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id', onupdate="CASCADE", ondelete="CASCADE"))
    event = db.relationship("Event", back_populates="competitions", single_parent=True)
    qualification_id = db.Column(db.Integer, db.ForeignKey('competition.competition_id',
                                                           onupdate="CASCADE", ondelete="CASCADE"))
    qualifications = db.relationship("Competition", backref=db.backref('qualification', remote_side=[competition_id]))

    def __repr__(self):
        return '{disc} {cls}'.format(cls=self.dancing_class, disc=self.discipline)

    def short_repr(self):
        return f'{self.discipline.name[:2]}{self.dancing_class.name[:2]}'

    def first_round(self):
        try:
            return Round.query.get(min([r.round_id for r in self.rounds]))
        except ValueError:
            return None

    def last_round(self):
        try:
            return Round.query.get(max([r.round_id for r in self.rounds]))
        except ValueError:
            return None

    def has_adjudicators(self):
        return len(self.adjudicators) > 0

    def result(self, follows=False):
        return CompetitionResult(self, follows=follows)

    def has_contestants(self):
        if self.mode == CompetitionMode.single_partner:
            return len(self.couples) > 0
        else:
            return len(self.leads) > 0 and len(self.follows) > 0

    def equal_leads_follows(self):
        if self.mode != CompetitionMode.single_partner:
            return len(self.leads) == len(self.follows)
        else:
            return True

    def can_create_first_round(self):
        return len(self.adjudicators) > 0 and self.has_contestants() and not self.has_rounds() \
               and self.equal_leads_follows()

    def max_couples(self):
        return max(len(self.couples), len(self.leads), len(self.follows))

    def generate_couples(self):
        if self.mode == CompetitionMode.single_partner:
            return self.couples
        elif self.mode == CompetitionMode.random_single_partner:
            return create_couples_list(leads=self.leads, follows=self.follows)
        elif self.mode == CompetitionMode.change_per_round or self.mode == CompetitionMode.change_per_dance:
            return create_couples_list(leads=self.leads, follows=self.follows)

    def is_random_single_partner(self):
        return self.mode == CompetitionMode.random_single_partner

    def is_change_per_round(self):
        return self.mode == CompetitionMode.change_per_round

    def is_change_per_dance(self):
        return self.mode == CompetitionMode.change_per_dance

    def has_rounds(self):
        return len(self.rounds) > 0

    def change_per_round_partner_list(self):
        rounds = [r for r in self.rounds]
        leads = {l: {r: '-' for r in self.rounds} for l in sorted([l.number for l in self.leads])}
        follows = {f: {r: '-' for r in self.rounds} for f in sorted([f.number for f in self.follows])}
        for r in self.rounds:
            for couple in r.couples:
                leads[couple.lead.number][r] = couple.follow.number
                follows[couple.follow.number][r] = couple.lead.number
        return leads, follows, rounds

    def is_configurable(self):
        if self.first_round() is None:
            return True
        else:
            return not self.first_round().has_heats()

    def competitors(self, numbers_only=False):
        if not numbers_only:
            if self.mode == CompetitionMode.single_partner:
                return f"{len(self.couples)} couple{'' if len(self.couples) == 1 else 's'}"
            else:
                return f"{len(self.leads)} lead{'' if len(self.leads) == 1 else 's'} / {len(self.follows)} " \
                    f"follow{'' if len(self.follows) == 1 else 's'}"
        else:
            if self.mode == CompetitionMode.single_partner:
                return f"{len(self.couples)}"
            else:
                return f"{len(self.leads)}/{len(self.follows)}"

    def dancers(self):
        return [d for d in self.leads + self.follows]


def create_couples_list(couples=None, leads=None, follows=None):
    if couples is not None:
        leads = [c.lead for c in couples]
        follows = [c.follow for c in couples]
    else:
        leads = [d for d in leads]
        follows = [d for d in follows]
    random.shuffle(leads)
    random.shuffle(follows)
    dancers = zip(leads, follows)
    couples = []
    for d in dancers:
        couple = Couple.query.filter(Couple.lead == d[0], Couple.follow == d[1]).first()
        if couple is None:
            couple = Couple()
            couple.number = d[0].number
            couple.lead = d[0]
            couple.follow = d[1]
            db.session.add(couple)
        couples.append(couple)
    db.session.commit()
    return couples


class DancingClass(db.Model):
    __tablename__ = TABLE_DANCING_CLASS
    dancing_class_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    competitions = db.relationship("Competition", back_populates="dancing_class")

    def __repr__(self):
        return '{}'.format(self.name)

    def has_competitions(self):
        return len(self.competitions) > 0

    def deletable(self):
        return not self.has_competitions()


class Discipline(db.Model):
    __tablename__ = TABLE_DISCIPLINE
    discipline_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    competitions = db.relationship("Competition", back_populates="discipline")
    dances = db.relationship("Dance", back_populates="discipline")

    def __repr__(self):
        return '{}'.format(self.name)

    def has_competitions(self):
        return len(self.competitions) > 0

    def has_dances(self):
        return len(self.dances) > 0

    def deletable(self):
        return not self.has_competitions() and not self.has_dances()


round_dance_table = db.Table(
    TABLE_ROUND_DANCE, db.Model.metadata,
    db.Column('round_id', db.Integer, db.ForeignKey('round.round_id',  onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('dance_id', db.Integer, db.ForeignKey('dance.dance_id',  onupdate="CASCADE", ondelete="CASCADE")),
    db.UniqueConstraint('round_id', 'dance_id', name='_round_dance_uc')
)

round_couple_table = db.Table(
    TABLE_ROUND_COUPLE, db.Model.metadata,
    db.Column('round_id', db.Integer, db.ForeignKey('round.round_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('couple_id', db.Integer, db.ForeignKey('couple.couple_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.UniqueConstraint('round_id', 'couple_id', name='_round_couple_uc')
)


heat_couple_table = db.Table(
    TABLE_HEAT_COUPLE, db.Model.metadata,
    db.Column('heat_id', db.Integer, db.ForeignKey('heat.heat_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('couple_id', db.Integer, db.ForeignKey('couple.couple_id', onupdate="CASCADE", ondelete="CASCADE")),
    db.UniqueConstraint('heat_id', 'couple_id', name='_heat_couple_uc')
)


class Dance(db.Model):
    __tablename__ = TABLE_DANCE
    dance_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    tag = db.Column(db.String(6), unique=True)
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.discipline_id',
                                                        onupdate="CASCADE", ondelete="CASCADE"))
    discipline = db.relationship("Discipline", back_populates="dances")

    def __repr__(self):
        return '{}'.format(self.name)

    def has_discipline(self):
        return self.discipline is not None

    def deletable(self):
        return not self.has_discipline()


class Adjudicator(db.Model):
    __tablename__ = TABLE_ADJUDICATOR
    adjudicator_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    tag = db.Column(db.String(6), unique=True)
    dance = db.Column(db.Integer, nullable=False, default=0)
    round = db.Column(db.Integer, nullable=False, default=0)
    competitions = db.relationship("Competition", secondary=competition_adjudicator_table,
                                   back_populates="adjudicators")

    def __repr__(self):
        return '{}'.format(self.name)

    def has_assignments(self):
        return len(self.competitions) > 0

    def assignments(self):
        return len(self.competitions)

    def assignments_on_day(self, date):
        return len([c for c in self.competitions if c.when.date() == date])

    def deletable(self):
        return len(self.competitions) == 0


class Dancer(db.Model):
    __tablename__ = TABLE_DANCER
    __table_args__ = (db.UniqueConstraint('number', 'role', name='_number_role_uc'),)
    dancer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    number = db.Column(db.Integer)
    role = db.Column(db.String(128))
    team = db.Column(db.String(128))
    couples_lead = db.relationship("Couple", foreign_keys="Couple.lead_id", back_populates="lead")
    couples_follow = db.relationship("Couple", foreign_keys="Couple.follow_id", back_populates="follow")
    competitions_lead = db.relationship("Competition", secondary=competition_lead_table, back_populates="leads")
    competitions_follow = db.relationship("Competition", secondary=competition_follow_table, back_populates="follows")
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'))
    contestant = db.relationship('Contestant', back_populates='dancers', uselist=False)

    def __repr__(self):
        return f'{self.name}'

    def partners(self):
        if self.role == LEAD:
            return [(c.follow, c.participating_competitions()) for c in self.couples_lead]
        else:
            return [(c.lead, c.participating_competitions()) for c in self.couples_follow]

    def couples(self):
        if self.role == LEAD:
            return self.couples_lead
        else:
            return self.couples_follow

    def competitions(self):
        if self.role == LEAD:
            return self.competitions_lead
        else:
            return self.competitions_follow

    def contestant_team(self):
        if self.contestant is not None:
            return self.contestant.contestant_info.team
        else:
            return None

    def deletable(self):
        return len(self.competitions_lead) + len(self.competitions_follow) + \
               len(self.couples_lead) + len(self.couples_follow) == 0

    def append_competition(self, comp):
        if comp is not None:
            if comp.mode != CompetitionMode.single_partner:
                if self.role == LEAD:
                    if comp not in self.competitions_lead:
                        self.competitions_lead.append(comp)
                else:
                    if comp not in self.competitions_follow:
                        self.competitions_follow.append(comp)

    def set_competitions(self, comps):
        if self.role == LEAD:
            self.competitions_lead = comps
        else:
            self.competitions_follow = comps


class Couple(db.Model):
    __tablename__ = TABLE_COUPLE
    __table_args__ = (db.UniqueConstraint('lead_id', 'follow_id', name='_lead_follow_uc'),)
    couple_id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    lead_id = db.Column(db.Integer, db.ForeignKey('dancer.dancer_id', onupdate="CASCADE", ondelete="CASCADE"))
    lead = db.relationship("Dancer", back_populates="couples_lead", foreign_keys="Couple.lead_id")
    follow_id = db.Column(db.Integer, db.ForeignKey('dancer.dancer_id', onupdate="CASCADE", ondelete="CASCADE"))
    follow = db.relationship("Dancer",  back_populates="couples_follow", foreign_keys="Couple.follow_id")
    competitions = db.relationship("Competition", secondary=competition_couple_table, back_populates="couples")
    rounds = db.relationship("Round", secondary=round_couple_table, back_populates="couples")
    heats = db.relationship("Heat", secondary=heat_couple_table)

    def __repr__(self):
        return '{number} - {lead} - {follow}'.format(number=self.number, lead=self.lead, follow=self.follow)

    def participating_competitions(self):
        if len(self.competitions) > 0:
            return [c for c in self.competitions if c.dancing_class.name != TEST]
        else:
            return list(set([r.competition for r in self.rounds + [h.round for h in self.heats]]))

    def deletable(self):
        return len(self.rounds) == 0 and len(self.heats) == 0


class RoundType(enum.Enum):
    qualification = "Qualification"
    general_look = "General look"
    first_round = "First round"
    re_dance = "Re-dance"
    second_round = "Second round"
    intermediate_round = "Intermediate round"
    semi_final = "Semi-final"
    final = "Final"


class Round(db.Model):
    __tablename__ = TABLE_ROUND
    round_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(RoundType))
    min_marks = db.Column(db.Integer, default=1)
    max_marks = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.competition_id',
                                                         onupdate="CASCADE", ondelete="CASCADE"))
    competition = db.relationship("Competition", back_populates="rounds")
    dances = db.relationship("Dance", secondary=round_dance_table)
    couples = db.relationship("Couple", secondary=round_couple_table, back_populates="rounds")
    heats = db.relationship("Heat", back_populates="round", cascade='all, delete, delete-orphan')
    round_results = db.relationship("RoundResult", back_populates="round", cascade='all, delete, delete-orphan')
    dance_active = db.relationship("DanceActive", back_populates="round", cascade='all, delete, delete-orphan')
    final_placings = db.relationship("FinalPlacing", back_populates="round", cascade='all, delete, delete-orphan')

    def __repr__(self):
        return '{comp} {type}'.format(comp=self.competition, type=self.type.value)

    def is_completed(self):
        if not self.is_final():
            return len(self.round_results) > 0
        else:
            return self.final_completed()

    def final_completed(self):
        placings = list(range(1, len(self.couples) + 1))
        for dance in self.dances:
            for adjudicator in self.competition.adjudicators:
                adjudicator_placings = \
                    sorted([final_placing.final_placing for final_placing in self.final_placings
                            if final_placing.adjudicator == adjudicator and final_placing.dance == dance
                            and final_placing.final_placing is not None])
                if placings != adjudicator_placings:
                    return False
        return not self.is_active

    def previous_round(self):
        previous_rounds = [r.round_id for r in self.competition.rounds if r.round_id < self.round_id]
        try:
            previous_rounds = [r for r in self.competition.rounds if r.round_id == max(previous_rounds)]
        except ValueError:
            return None
        else:
            return previous_rounds[0]

    def first_round_after_qualification_split(self):
        return self.type == RoundType.first_round and len(self.heats) == 0 \
               and self.competition.qualification is not None

    def is_general_look(self):
        return self.type == RoundType.general_look

    def is_qualification(self):
        return self.type == RoundType.qualification

    def is_first_round(self):
        return self.type == RoundType.first_round

    def is_re_dance(self):
        return self.type == RoundType.re_dance

    def is_second_round(self):
        return self.type == RoundType.second_round

    def is_intermediate_round(self):
        return self.type == RoundType.intermediate_round

    def is_semi_final(self):
        return self.type == RoundType.semi_final

    def is_final(self):
        return self.type == RoundType.final

    def round_completed(self):
        return len(self.round_results) > 0

    def is_split(self):
        return sum([len(c.rounds) for c in [q for q in self.competition.qualifications]]) > 0

    def has_adjudicators(self):
        return len(self.competition.adjudicators) > 0

    def first_dance(self):
        dances = [d for d in self.dances if d.name in DANCE_ORDER[self.competition.discipline.name]]
        try:
            dances.sort(key=lambda x: DANCE_ORDER[self.competition.discipline.name][x.name])
            return dances[0]
        except KeyError:
            return None
        except IndexError:
            return None

    def previous_dance(self, dance):
        dances = [d for d in self.dances if d.dance_id < dance.dance_id]
        try:
            dances.sort(key=lambda x: DANCE_ORDER[self.competition.discipline.name][x.name])
            return dances[-1]
        except KeyError:
            return None
        except IndexError:
            return None

    def next_dance(self, dance):
        dances = [d for d in self.dances if d.dance_id > dance.dance_id]
        try:
            dances.sort(key=lambda x: DANCE_ORDER[self.competition.discipline.name][x.name])
            return dances[0]
        except KeyError:
            return None
        except IndexError:
            return None

    def last_dance(self):
        dances = [d for d in self.dances]
        try:
            dances.sort(key=lambda x: DANCE_ORDER[self.competition.discipline.name][x.name])
            return dances[-1]
        except KeyError:
            return None
        except IndexError:
            return None

    def has_dance(self, dance_id):
        return dance_id in [d.dance_id for d in self.dances]

    def has_dances(self):
        return len(self.dances) > 0

    def is_dance_active(self, dance):
        return [d for d in self.dance_active if d.dance == dance][0].is_active

    def number_of_heats(self, dance):
        return len([h for h in self.heats if h.dance == dance])

    def has_heats(self):
        return len(self.heats)

    def has_next_round(self):
        return any(r.round_id > self.round_id for r in self.competition.rounds)

    def adjudicator_marks(self, adjudicator, dance):
        marks = []
        for heat in self.heats:
            if heat.dance == dance:
                marks.extend([m for m in heat.marks if m.adjudicator == adjudicator])
        marks.sort(key=lambda x: x.couple.number)
        return marks

    def dance_lead_follow_list(self):
        lead_follow_list = {d.tag: {} for d in self.dances}
        for dance in self.dances:
            heats = [heat for heat in self.heats if heat.dance == dance]
            lead_follow = {couple.number: couple.follow.number for heat in heats for couple in heat.couples}
            follow_lead = {couple.follow.number: couple.number for heat in heats for couple in heat.couples}
            lead_follow_list[dance.tag].update(lead_follow)
            lead_follow_list[dance.tag].update(follow_lead)
        return lead_follow_list

    def dance_heat_list(self):
        dance_heats = {}
        for dance in self.dances:
            heats = [heat for heat in self.heats if heat.dance == dance]
            couple_heat = {couple.number: heat.number for heat in heats for couple in heat.couples}
            dance_heats.update({dance.tag: couple_heat})
        return dance_heats

    def adjudicator_mark_list(self):
        adjudicator_marks = [{'adjudicator': adjudicator.name,
                              'marks': {str(dance.dance_id): self.adjudicator_marks(adjudicator, dance)
                                        for dance in self.dances}}
                             for adjudicator in self.competition.adjudicators]
        return adjudicator_marks

    def split_couples_into_heats(self, heats):
        n = len(self.couples)
        k = heats
        if self.competition.mode == CompetitionMode.change_per_dance:
            couples = [c for c in create_couples_list(couples=self.couples)]
        else:
            couples = [c for c in self.couples]
        shuffle(couples)
        return [couples[i * (n // k) + min(i, n % k):(i + 1) * (n // k) + min(i + 1, n % k)] for i in range(k)]

    def create_heats(self, heats):
        for dance in self.dances:
            couples = self.split_couples_into_heats(heats)
            for idx, c in enumerate(couples, start=1):
                heat = Heat()
                heat.dance = dance
                heat.couples = c
                heat.number = idx
                self.heats.append(heat)
                for couple in c:
                    present = CouplePresent()
                    present.couple = couple
                    present.present = False
                    heat.couples_present.append(present)
                    for adj in self.competition.adjudicators:
                        mark = Mark()
                        mark.adjudicator = adj
                        mark.couple = couple
                        heat.marks.append(mark)
        db.session.commit()

    def create_final(self):
        for dance in self.dances:
            heat = Heat()
            heat.dance = dance
            if self.competition.mode == CompetitionMode.change_per_dance:
                heat.couples = create_couples_list(couples=self.couples)
            else:
                heat.couples = self.couples
            heat.number = 1
            self.heats.append(heat)
            for adj in self.competition.adjudicators:
                for couple in heat.couples:
                    final_placing = FinalPlacing()
                    final_placing.adjudicator = adj
                    final_placing.couple = couple
                    final_placing.dance = dance
                    self.final_placings.append(final_placing)
        db.session.commit()

    def get_cutoffs(self):
        round_result_list = [r.marks for r in self.round_results if r.marks != -1]
        round_result_list.sort()
        unique_results = list(set(round_result_list))
        unique_results.sort(reverse=True)
        return [(-1, f"all couples")] + [(r, f"{r} marks") for r in unique_results]

    def change_per_dance_dancers_rows(self):
        round_result_list = [r for r in self.marks()]
        leads = [c.lead for c in self.couples]
        follows = [c.follow for c in self.couples]
        results = {d: 0 for d in leads + follows}
        if self.type == RoundType.re_dance:
            directly_qualified_leads = [c for c in self.competition.leads if c not in leads]
            directly_qualified_follows = [c for c in self.competition.follows if c not in follows]
            results.update({d: -1 for d in directly_qualified_leads})
            results.update({d: -1 for d in directly_qualified_follows})
        for mark in round_result_list:
            results[mark.couple.lead] += 1 if mark.mark else 0
            results[mark.couple.follow] += 1 if mark.mark else 0
        dancers_list = [{'dancer': d, 'place': None, 'crosses': results[d], 'lead': d.role == LEAD,
                         'follow': d.role == FOLLOW, 'team': d.team} for d in results]
        dancers_list.sort(key=lambda x: (x['crosses'] != -1, -x['crosses'], not x['lead'], x['dancer'].number))
        unique_results = list(set([d['crosses'] for d in dancers_list]))
        unique_results.sort(key=lambda x: (x != -1, -x))
        result_placing = {}
        for i in unique_results:
            result_placing.update({i: [d['crosses'] for d in dancers_list].count(i)})
        result_map = {}
        counter = 1
        for i in unique_results:
            if result_placing[i] == 1:
                result_map.update({i: str(counter)})
            else:
                result_map.update({i: str(counter) + ' - ' + str(counter + result_placing[i] - 1)})
            counter += result_placing[i]
        for d in dancers_list:
            d['placing'] = result_map[d['crosses']]
        return dancers_list

    def get_cutoffs_for_change_per_dance(self):
        dancers_list = self.change_per_dance_dancers_rows()
        unique_results = list(set([d['crosses'] for d in dancers_list]))
        unique_results = [u for u in unique_results if u != -1]
        unique_results.sort(reverse=True)
        viable_unique_results = []
        for r in unique_results:
            dancers = [d for d in dancers_list if d['crosses'] >= r]
            if len([d for d in dancers if d['lead']]) == len([d for d in dancers if d['follow']]):
                viable_unique_results.append(r)
        return [(-1, f"all couples")] + [(r, f"{r} marks") for r in viable_unique_results]

    def adjudicator_dance_marks(self, adjudicator, dance):
        marks = list(itertools.chain.from_iterable([h.marks for h in self.heats if h.dance == dance]))
        return [m for m in marks if m.adjudicator == adjudicator]

    def adjudicator_dance_marked(self, adjudicator, dance):
        marks = self.adjudicator_dance_marks(adjudicator, dance)
        return [m for m in marks if m.adjudicator == adjudicator and m.mark]

    def adjudicator_dance_noted(self, adjudicator, dance):
        marks = self.adjudicator_dance_marks(adjudicator, dance)
        return [m for m in marks if m.adjudicator == adjudicator and m.notes > 0]

    def adjudicator_dance_placed(self, adjudicator, dance):
        placings = [p for p in self.final_placings if p.adjudicator == adjudicator and p.dance == dance]
        return [p for p in placings if p.final_placing in list(range(1, len(self.couples) + 1))]

    def adjudicator_dance_to_dict(self, adjudicator, dance):
        data = {
            'crossed': len(self.adjudicator_dance_marked(adjudicator, dance)),
            'couples': len(self.couples),
            'noted': len(self.adjudicator_dance_noted(adjudicator, dance)),
            'min_marks': self.min_marks,
            'max_marks': self.max_marks,
            'open': self.is_dance_active(dance),
        }
        return data

    def adjudicator_dance_final_to_dict(self, adjudicator, dance):
        data = {
            'placed': len(self.round.adjudicator_dance_placed(adjudicator, dance)),
            'couples': len(self.round.couples),
            'open': self.round.is_dance_active(self.dance),
        }
        return data

    def marks(self, dance=None):
        marks = []
        for heat in self.heats:
            if dance is not None:
                if heat.dance == dance:
                    for mark in heat.marks:
                        marks.append(mark)
            else:
                for mark in heat.marks:
                    marks.append(mark)
        return marks

    def has_one_heat(self):
        return len(self.dances) == len(self.heats)

    def dance_skating(self, dance):
        return SkatingDance(dancing_round=self, dance=dance)

    def skating_summary(self, follows=False):
        return SkatingSummary(dancing_round=self, follows=follows)

    def deactivate(self):
        for dance in self.dance_active:
            dance.is_active = False
        self.is_active = False
        db.session.commit()

    def is_place_given(self, adjudicator, dance, place):
        for placing in [p for p in self.final_placings if p.adjudicator == adjudicator and p.dance == dance]:
            if placing.final_placing == place:
                return True
        return False

    def adjudicators_present(self, dance):
        return [a for a in self.competition.adjudicators if a.round == self.round_id and a.dance == dance.dance_id]

    def adjudicators_missing(self, dance):
        return [a for a in self.competition.adjudicators
                if not a.round == self.round_id or not a.dance == dance.dance_id]

    def previous_rounds(self):
        return sorted([r for r in self.competition.rounds if r.round_id < self.round_id], key=lambda x: x.round_id,
                      reverse=True)

    def previous_rounds_dancers_rows(self):
        couples_placed = [c.number for c in self.couples]
        rounds = self.previous_rounds()
        total_results = []
        for r in rounds:
            round_results_list = [result for result in r.round_results if result.couple.number not in couples_placed]
            dancers_list = [{'result': r, 'placing': None, 'crosses': r.marks} for r in round_results_list]
            dancers_list.sort(key=lambda x: (-x['crosses'], x['result'].couple.number))
            unique_results = list(set([d['crosses'] for d in dancers_list]))
            unique_results.sort(reverse=True)
            result_placing = {}
            for i in unique_results:
                result_placing.update({i: [d['crosses'] for d in dancers_list].count(i)})
            result_map = {}
            counter = 1 + len(couples_placed)
            for i in unique_results:
                if result_placing[i] == 1:
                    result_map.update({i: str(counter)})
                else:
                    result_map.update({i: str(counter) + ' - ' + str(counter + result_placing[i] - 1)})
                counter += result_placing[i]
            for d in dancers_list:
                d['placing'] = result_map[d['crosses']]
            total_results.extend(dancers_list)
            couples_placed.extend([result.couple.number for result in r.round_results
                                   if result.couple.number not in couples_placed])
        return total_results

    def previous_rounds_change_per_dance_dancers_rows(self, leads_only=False, follows_only=False):
        leads_placed = [] if follows_only else [c.lead for c in self.couples]
        follows_placed = [] if leads_only else [c.follow for c in self.couples]
        dancers_placed = leads_placed + follows_placed
        rounds = self.previous_rounds()
        total_results = []
        for r in rounds:
            round_result_list = [m for m in r.marks()]
            leads = [c.lead for c in r.couples]
            follows = [c.follow for c in r.couples]
            results = {d: 0 for d in leads + follows}
            for mark in round_result_list:
                results[mark.couple.lead] += 1 if mark.mark else 0
                results[mark.couple.follow] += 1 if mark.mark else 0
            dancers_list = [{'dancer': d, 'place': None, 'crosses': results[d], 'lead': d.role == LEAD,
                             'follow': d.role == FOLLOW, 'team': d.team} for d in results if d not in dancers_placed]
            if leads_only:
                dancers_list = [d for d in dancers_list if d['lead']]
            if follows_only:
                dancers_list = [d for d in dancers_list if d['follow']]
            dancers_list.sort(key=lambda x: (x['crosses'] != -1, -x['crosses'], not x['lead'], x['dancer'].number))
            unique_results = list(set([d['crosses'] for d in dancers_list]))
            unique_results.sort(key=lambda x: (x != -1, -x))
            result_placing = {}
            for i in unique_results:
                result_placing.update({i: [d['crosses'] for d in dancers_list].count(i)})
            result_map = {}
            counter = 1 + len(dancers_placed)
            for i in unique_results:
                if result_placing[i] == 1:
                    result_map.update({i: str(counter)})
                else:
                    result_map.update({i: str(counter) + ' - ' + str(counter + result_placing[i] - 1)})
                counter += result_placing[i]
            for d in dancers_list:
                d['placing'] = result_map[d['crosses']]
            total_results.extend(dancers_list)
            dancers_placed.extend([d['dancer'] for d in dancers_list if d['dancer'] not in dancers_placed])
        return total_results

    def can_evaluate(self):
        for adjudicator in self.competition.adjudicators:
            for dance in self.dances:
                marks = [m.mark for m in self.adjudicator_marks(adjudicator, dance)]
                if True not in marks:
                    return False
        return True

    def evaluation_errors(self):
        errors_list = []
        for adjudicator in self.competition.adjudicators:
            for dance in self.dances:
                marks = [m.mark for m in self.adjudicator_marks(adjudicator, dance)]
                if True not in marks:
                    errors_list.append(f"{adjudicator} has zero marks in {dance}. This is probably an error.")
        return errors_list


class DanceActive(db.Model):
    __tablename__ = TABLE_DANCE_ACTIVE
    dance_active_id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.round_id', onupdate="CASCADE", ondelete="CASCADE"))
    round = db.relationship("Round", back_populates="dance_active")
    dance_id = db.Column(db.Integer, db.ForeignKey('dance.dance_id', onupdate="CASCADE", ondelete="CASCADE"))
    dance = db.relationship("Dance")

    def __repr__(self):
        return '{round} - {dance}'.format(round=self.round, dance=self.dance)


class Heat(db.Model):
    __tablename__ = TABLE_HEAT
    heat_id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, default=1)
    floor = db.Column(db.Integer, default=1)
    round_id = db.Column(db.Integer, db.ForeignKey('round.round_id', onupdate="CASCADE", ondelete="CASCADE"))
    round = db.relationship("Round", back_populates="heats")
    dance_id = db.Column(db.Integer, db.ForeignKey('dance.dance_id'))
    dance = db.relationship("Dance")
    couples = db.relationship("Couple", secondary=heat_couple_table)
    marks = db.relationship("Mark", back_populates="heat", cascade='all, delete, delete-orphan')
    couples_present = db.relationship("CouplePresent", back_populates="heat", cascade='all, delete, delete-orphan')

    def __repr__(self):
        return '{round} - {dance} - Heat {number}'.format(number=self.number, dance=self.dance, round=self.round)


class Mark(db.Model):
    __tablename__ = TABLE_MARK
    mark_id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Integer, default=0)
    adjudicator_id = db.Column(db.Integer, db.ForeignKey('adjudicator.adjudicator_id',
                                                         onupdate="CASCADE", ondelete="CASCADE"))
    adjudicator = db.relationship("Adjudicator")
    couple_id = db.Column(db.Integer, db.ForeignKey('couple.couple_id', onupdate="CASCADE", ondelete="CASCADE"))
    couple = db.relationship("Couple")
    heat_id = db.Column(db.Integer, db.ForeignKey('heat.heat_id', onupdate="CASCADE", ondelete="CASCADE"))
    heat = db.relationship("Heat", back_populates="marks")

    def __repr__(self):
        return '{round} - {dance} - {adj} - {couple}'\
            .format(couple=self.couple, adj=self.adjudicator.name, dance=self.heat.dance, round=self.heat.round)

    def to_dict(self):
        data = {
            'marked': self.mark,
            'notes': self.notes,
            'crossed': len(self.heat.round.adjudicator_dance_marked(self.adjudicator, self.heat.dance)),
            'couples': len(self.heat.round.couples),
            'noted': len(self.heat.round.adjudicator_dance_noted(self.adjudicator, self.heat.dance)),
            'min_marks': self.heat.round.min_marks,
            'max_marks': self.heat.round.max_marks,
            'open': self.heat.round.is_dance_active(self.heat.dance),
        }
        return data


class FinalPlacing(db.Model):
    __tablename__ = TABLE_FINAL_PLACING
    final_placing_id = db.Column(db.Integer, primary_key=True)
    final_placing = db.Column(db.Integer, default=0)
    adjudicator_id = db.Column(db.Integer, db.ForeignKey('adjudicator.adjudicator_id',
                                                         onupdate="CASCADE", ondelete="CASCADE"))
    adjudicator = db.relationship("Adjudicator")
    couple_id = db.Column(db.Integer, db.ForeignKey('couple.couple_id', onupdate="CASCADE", ondelete="CASCADE"))
    couple = db.relationship("Couple")
    round_id = db.Column(db.Integer, db.ForeignKey('round.round_id', onupdate="CASCADE", ondelete="CASCADE"))
    round = db.relationship("Round", back_populates="final_placings")
    dance_id = db.Column(db.Integer, db.ForeignKey('dance.dance_id', onupdate="CASCADE", ondelete="CASCADE"))
    dance = db.relationship("Dance")

    def __repr__(self):
        return '{round} - {dance} - {adj} - {couple}'\
            .format(couple=self.couple, adj=self.adjudicator.name, dance=self.dance, round=self.round)

    def to_dict(self):
        data = {
            'place': self.final_placing,
            'placed': len(self.round.adjudicator_dance_placed(self.adjudicator, self.dance)),
            'couples': len(self.round.couples),
            'open': self.round.is_dance_active(self.dance),
        }
        return data


class CouplePresent(db.Model):
    __tablename__ = TABLE_COUPLE_PRESENT
    couple_present_id = db.Column(db.Integer, primary_key=True)
    present = db.Column(db.Boolean, default=False)
    couple_id = db.Column(db.Integer, db.ForeignKey('couple.couple_id', onupdate="CASCADE", ondelete="CASCADE"))
    couple = db.relationship("Couple")
    heat_id = db.Column(db.Integer, db.ForeignKey('heat.heat_id', onupdate="CASCADE", ondelete="CASCADE"))
    heat = db.relationship("Heat", back_populates="couples_present")

    def __repr__(self):
        return '{round} - {dance} - {couple}'\
            .format(couple=self.couple, dance=self.heat.dance, round=self.heat.round)


class RoundResult(db.Model):
    __tablename__ = TABLE_ROUND_RESULT
    round_result_id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couple.couple_id', onupdate="CASCADE", ondelete="CASCADE"))
    couple = db.relationship("Couple")
    marks = db.Column(db.Integer, default=0)
    placing = db.Column(db.String(12))
    round_id = db.Column(db.Integer, db.ForeignKey('round.round_id', onupdate="CASCADE", ondelete="CASCADE"))
    round = db.relationship("Round", back_populates="round_results")

    def __repr__(self):
        return '{round} - {couple}'.format(couple=self.couple, round=self.round)
