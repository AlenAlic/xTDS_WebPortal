from ntds_webportal import db, login
from flask import current_app, url_for, redirect, render_template
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import ntds_webportal.data as data
from ntds_webportal.data import *
from raffle_system.raffle_config import *
from functools import wraps
from time import time
from datetime import datetime
import jwt
import json


USERS = 'users'
TEAMS = 'teams'
TEAM_FINANCES = 'team_finances'
NOTIFICATIONS = 'notifications'
EXCLUDED_FROM_CLEARING = [USERS, TEAMS, TEAM_FINANCES, NOTIFICATIONS]


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def requires_access_level(access_levels):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.access not in access_levels:
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# noinspection PyUnresolvedReferences
class User(UserMixin, db.Model):
    __tablename__ = USERS
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128), index=True)
    access = db.Column(db.Integer, index=True, nullable=False)
    is_active = db.Column(db.Boolean, index=True, nullable=False, default=False)
    send_new_messages_email = db.Column(db.Boolean, nullable=False, default=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    team = db.relationship('Team')

    def __repr__(self):
        return '{}'.format(self.username)

    def get_id(self):
        return self.user_id

    def is_admin(self):
        return self.access == data.ACCESS['admin']

    def is_organizer(self):
        return self.access == data.ACCESS['organizer']

    def is_tc(self):
        return self.access == data.ACCESS['team_captain']

    def is_treasurer(self):
        return self.access == data.ACCESS['treasurer']

    def is_bdo(self):
        return self.access == data.ACCESS['blind_date_organizer']

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
                    r.other.contestant_info[0].team == current_user.team])

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

    def teamcaptains_selected(self):
        if self.has_dancers_registered():
            return raffle_settings[MAX_TEAMCAPTAINS] - \
                   len(db.session.query(ContestantInfo).filter(ContestantInfo.team == current_user.team,
                                                               ContestantInfo.team_captain.is_(True)).all())
        else:
            return 0

    @staticmethod
    def has_dancers_registered():
        return len(db.session.query(Contestant).join(ContestantInfo)
                   .filter(ContestantInfo.team == current_user.team).all()) > 0


class Team(db.Model):
    __tablename__ = TEAMS
    team_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(128), nullable=False)
    city = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False, unique=True)
    finances = db.relationship('TeamFinances', back_populates='team')

    def __repr__(self):
        return '{}'.format(self.name)


class TeamFinances(db.Model):
    __tablename__ = TEAM_FINANCES
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), primary_key=True)
    team = db.relationship('Team', back_populates='finances')
    paid = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '{}'.format(self.team)


class Contestant(db.Model):
    __tablename__ = 'contestants'
    contestant_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    prefixes = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    contestant_info = db.relationship('ContestantInfo', back_populates='contestant', cascade='all, delete-orphan')
    dancing_info = db.relationship('DancingInfo', back_populates='contestant', cascade='all, delete-orphan')
    volunteer_info = db.relationship('VolunteerInfo', back_populates='contestant', cascade='all, delete-orphan')
    additional_info = db.relationship('AdditionalInfo', back_populates='contestant', cascade='all, delete-orphan')
    status_info = db.relationship('StatusInfo', back_populates='contestant', cascade='all, delete-orphan')
    merchandise_info = db.relationship('MerchandiseInfo', back_populates='contestant', cascade='all, delete-orphan')

    def __repr__(self):
        # return '{id} - {name}'.format(id=self.contestant_id, name=self.get_full_name())
        return '{name}'.format(name=self.get_full_name())

    def get_full_name(self):
        if self.prefixes is None or self.prefixes == '':
            return ' '.join((self.first_name, self.last_name))
        else:
            return ' '.join((self.first_name, self.prefixes, self.last_name))

    def capitalize_name(self):
        self.first_name.title()
        self.last_name.title()

    def competition(self, competition):
        return DancingInfo.query.filter_by(contestant_id=self.contestant_id, competition=competition).first()

    def cancel_registration(self):
        self.status_info[0].set_status(CANCELLED)
        for di in self.dancing_info:
            di.set_partner(None)
        self.contestant_info[0].team_captain = False
        db.session.commit()

    def get_dancing_info(self, competition):
        return next((di for di in self.dancing_info if di.competition == competition), None)


class ContestantInfo(db.Model):
    __tablename__ = 'contestant_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='contestant_info')
    number = db.Column(db.Integer, nullable=False)
    team_captain = db.Column(db.Boolean, nullable=False, default=False)
    student = db.Column(db.Boolean, index=True, nullable=False, default=False)
    first_time = db.Column(db.Boolean, index=True, nullable=False, default=False)
    diet_allergies = db.Column('Diet/Allergies', db.String(512), nullable=True, default=None)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)
    team = db.relationship('Team')

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def set_teamcaptain(self):
        current_tc = db.session.query(Contestant).join(ContestantInfo) \
            .filter(ContestantInfo.team == current_user.team, ContestantInfo.team_captain.is_(True)).first()
        if current_tc is not None:
            current_tc.contestant_info[0].team_captain = False
        self.team_captain = True
        db.session.commit()


class DancingInfo(db.Model):
    __tablename__ = 'dancing_info'
    __table_args__ = (db.UniqueConstraint('contestant_id', 'competition', 'level'),)
    contest_id = db.Column(db.Integer, primary_key=True)
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'))
    contestant = db.relationship('Contestant', foreign_keys=contestant_id)
    competition = db.Column(db.String(128), nullable=False)
    level = db.Column(db.String(128), nullable=False, default=data.NO)
    role = db.Column(db.String(128), nullable=False, default=data.NO)
    blind_date = db.Column(db.Boolean, nullable=False, default=False)
    partner = db.Column(db.Integer, nullable=True, default=None)

    def __repr__(self):
        return '{competition}: {name}'.format(competition=self.competition, name=self.contestant)

    def valid_match(self, other):
        errors = []
        if self.level in BLIND_DATE_LEVELS or other.level in BLIND_DATE_LEVELS:
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
        partner = db.session.query(DancingInfo) \
            .filter_by(contestant_id=contestant_id if contestant_id is not None else self.partner,
                       competition=self.competition, level=self.level).first()
        if contestant_id is not None:
            if partner is not None:
                partner.partner = self.contestant_id
                self.partner = partner.contestant_id
        else:
            if partner is not None:
                partner.partner = None
            self.partner = None
        db.session.commit()

    def not_dancing(self, competition):
        self.competition = competition
        self.level = data.NO
        self.role = data.NO
        self.blind_date = False
        self.partner = None


class VolunteerInfo(db.Model):
    __tablename__ = 'volunteer_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='volunteer_info')
    volunteer = db.Column(db.String(16), nullable=False)
    first_aid = db.Column(db.String(16), nullable=False)
    jury_ballroom = db.Column(db.String(16), nullable=False)
    jury_latin = db.Column(db.String(16), nullable=False)
    license_jury_ballroom = db.Column(db.String(16), nullable=False)
    license_jury_latin = db.Column(db.String(16), nullable=False)
    jury_salsa = db.Column(db.String(16), nullable=False)
    jury_polka = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def not_volunteering(self):
        self.volunteer = data.NO
        self.first_aid = data.NO
        self.jury_ballroom = data.NO
        self.jury_latin = data.NO
        self.license_jury_ballroom = data.NO
        self.license_jury_latin = data.NO
        self.jury_salsa = data.NO
        self.jury_polka = data.NO


class AdditionalInfo(db.Model):
    __tablename__ = 'additional_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='additional_info')
    sleeping_arrangements = db.Column(db.Boolean, nullable=False)
    t_shirt = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)


class StatusInfo(db.Model):
    __tablename__ = 'status_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='status_info')
    status = db.Column(db.String(16), index=True, default=data.REGISTERED)
    payment_required = db.Column(db.Boolean, index=True, nullable=False, default=False)
    paid = db.Column(db.Boolean, index=True, nullable=False, default=False)
    raffle_status = db.Column(db.String(16), index=True, default=data.REGISTERED)
    guaranteed_entry = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def set_status(self, status=None):
        if status is not None:
            self.status = status
            self.raffle_status = status
        else:
            self.status = self.raffle_status
        if self.status == data.CONFIRMED:
            self.payment_required = True
        elif self.status == data.REGISTERED:
            self.payment_required = False


class MerchandiseInfo(db.Model):
    __tablename__ = 'merchandise_info'
    order_id = db.Column(db.Integer, primary_key=True)
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'))
    contestant = db.relationship('Contestant', back_populates='merchandise_info')
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)


class Merchandise(db.Model):
    __tablename__ = 'merchandise'
    merchandise_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(128), nullable=False)
    product_description = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '{name}'.format(name=self.product_name)


class Notification(db.Model):
    __tablename__ = NOTIFICATIONS
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    unread = db.Column(db.Boolean, index=True, default=True)
    archived = db.Column(db.Boolean, index=True, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
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


class PartnerRequest(db.Model):
    STATE = {'Open': 1, 'Accepted': 2, 'Rejected': 3, 'Cancelled': 4}
    STATE_NAMES = {v: k for k, v in STATE.items()}

    __tablename__ = 'partner_request'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    remark = db.Column(db.Text())
    response = db.Column(db.Text())
    level = db.Column(db.String(128), nullable=False, default=data.NO)
    competition = db.Column(db.String(128), nullable=False, default=data.BREITENSPORT)
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
        recipients = User.query.filter_by(team=self.dancer.contestant_info[0].team)
        for u in recipients:
            n = Notification()
            n.title = f"{self.state_name()} - Partner request: {self.dancer.get_full_name()} with " \
                      f"{self.other.get_full_name()} in {self.competition}"
            n.user = u
            n.text = render_template('notifications/partner_request.html', request=self)
            db.session.add(n)
        db.session.commit()

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
        self.notify()
        self.state = self.STATE['Accepted']
        self.contestant.first_name = self.first_name
        self.contestant.last_name = self.last_name
        self.contestant.prefixes = self.prefixes

    def reject(self):
        self.state = self.STATE['Rejected']
        self.notify()

    def notify(self):
        recipients = User.query.filter_by(team=self.contestant.contestant_info[0].team)
        for u in recipients:
            n = Notification()
            n.title = f"{self.state_name()} - Name change request: " \
                      f"{self.contestant.get_full_name()} to {self.get_full_name()}"
            n.user = u
            n.text = render_template('notifications/name_change_request.html', request=self)
            db.session.add(n)
        db.session.commit()

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
    __tablename__ = 'tournament_state'
    lock = db.Column(db.Integer, primary_key=True)
    main_raffle_taken_place = db.Column(db.Boolean, nullable=False, default=False)
    main_raffle_result_visible = db.Column(db.Boolean, nullable=False, default=False)
    numbers_rearranged = db.Column(db.Boolean, nullable=False, default=False)
    raffle_completed_message_sent = db.Column(db.Boolean, nullable=False, default=False)
    tournament_config = db.Column(db.String(2048), nullable=False)
    raffle_config = db.Column(db.String(2048), nullable=False)

    def __repr__(self):
        return 'Tournament config'

    def set_raffle_config(self, c):
        self.raffle_config = json.dumps(c)

    def get_raffle_config(self):
        rc = json.loads(self.raffle_config)
        for k, v in rc.items():
            try:
                rc[k] = int(v)
            except ValueError:
                pass
        return rc
    
    def update_raffle_config(self, key, value):
        tc = self.get_raffle_config()
        tc[key] = value
        db.session.commit()

    def get_raffle_config_value(self, key):
        return self.get_raffle_config()[key]
    
    def set_tournament_config(self, c):
        self.tournament_config = json.dumps(c)

    def get_tournament_config(self):
        return json.loads(self.tournament_config)

    def update_tournament_config(self, key, value):
        tc = self.get_tournament_config()
        tc[key] = value
        db.session.commit()

    def get_tournament_config_value(self, key):
        return self.get_tournament_config()[key]
