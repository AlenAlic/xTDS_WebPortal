from ntds_webportal import db, login
from functools import wraps
from flask import current_app, url_for, redirect
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
from datetime import datetime
import jwt
import ntds_webportal.data as data


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


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128), index=True)
    access = db.Column(db.Integer, index=True, nullable=False)
    is_active = db.Column(db.Boolean, index=True, nullable=False, default=False)
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
        return jwt.encode({'reset_password': self.user_id, 'exp': time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def unread_notifications(self):
        return Notification.query.filter_by(user=self, unread=True).count()

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except jwt.exceptions.InvalidTokenError:
            return 'error'
        return User.query.get(user_id)


class Team(db.Model):
    __tablename__ = 'teams'
    team_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False, unique=True)

    def __repr__(self):
        return '{}'.format(self.name)


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

    def __repr__(self):
        return '{id} - {name}'.format(id=self.contestant_id, name=self.get_full_name())

    def get_full_name(self):
        if self.prefixes is None or self.prefixes == '':
            return ' '.join((self.first_name, self.last_name))
        else:
            return ' '.join((self.first_name, self.prefixes, self.last_name))

    def capitalize_name(self):
        self.first_name.title()
        self.last_name.title()


class ContestantInfo(db.Model):
    __tablename__ = 'contestant_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='contestant_info')
    number = db.Column(db.Integer, nullable=False)
    team_captain = db.Column(db.Boolean, nullable=False, default=False)
    student = db.Column(db.Boolean, index=True, nullable=False, default=False)
    diet_allergies = db.Column('Diet/Allergies', db.String(512), nullable=True, default=None)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)
    team = db.relationship('Team')

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def set_teamcaptain(self):
        current_tc = db.session.query(Contestant).join(ContestantInfo) \
            .filter(ContestantInfo.team_captain.is_(True)).first()
        if current_tc is not None:
            current_tc.contestant_info[0].team_captain = False
        self.team_captain = True
        db.session.commit()


class DancingInfo(db.Model):
    __tablename__ = 'dancing_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='dancing_info', foreign_keys=contestant_id)
    ballroom_level = db.Column(db.String(128), nullable=False, default=data.NO)
    ballroom_role = db.Column(db.String(128), nullable=False, default=data.NO)
    ballroom_blind_date = db.Column(db.Boolean, nullable=False, default=False)
    ballroom_partner = db.Column(db.Integer, nullable=True, default=None)
    latin_level = db.Column(db.String(128), nullable=False, default=data.NO)
    latin_role = db.Column(db.String(128), nullable=False, default=data.NO)
    latin_blind_date = db.Column(db.Boolean, nullable=False, default=False)
    latin_partner = db.Column(db.Integer, nullable=True, default=None)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def not_dancing_ballroom(self):
        self.ballroom_level = data.NO
        self.ballroom_role = data.NO
        self.ballroom_blind_date = False
        self.ballroom_partner = None

    def not_dancing_latin(self):
        self.latin_level = data.NO
        self.latin_role = data.NO
        self.latin_blind_date = False
        self.latin_partner = None

    def set_ballroom_partner(self, contestant_id):
        if contestant_id is not None:
            partner = db.session.query(DancingInfo).filter_by(contestant_id=contestant_id).first()
            partner.ballroom_partner = self.contestant_id
            self.ballroom_partner = partner.contestant_id
        else:
            partner = db.session.query(DancingInfo).filter_by(ballroom_partner=self.contestant_id).first()
            if partner is not None:
                partner.ballroom_partner = None
            self.ballroom_partner = None
        db.session.commit()

    def set_latin_partner(self, contestant_id):
        if contestant_id is not None:
            partner = db.session.query(DancingInfo).filter_by(contestant_id=contestant_id).first()
            partner.latin_partner = self.contestant_id
            self.latin_partner = partner.contestant_id
        else:
            partner = db.session.query(DancingInfo).filter_by(latin_partner=self.contestant_id).first()
            if partner is not None:
                partner.latin_partner = None
            self.latin_partner = None
        db.session.commit()


class VolunteerInfo(db.Model):
    __tablename__ = 'volunteer_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    contestant = db.relationship('Contestant', back_populates='volunteer_info')
    volunteer = db.Column(db.String(16), nullable=False)
    first_aid = db.Column(db.String(16), nullable=False)
    jury_ballroom = db.Column(db.String(16), nullable=False)
    jury_latin = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def not_volunteering(self):
        self.volunteer = data.NO
        self.first_aid = data.NO
        self.jury_ballroom = data.NO
        self.jury_latin = data.NO


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
    first_time = db.Column(db.Boolean, index=True, nullable=False, default=False)
    payment_required = db.Column(db.Boolean, index=True, nullable=False, default=False)
    paid = db.Column(db.Boolean, index=True, nullable=False, default=False)

    # name_change_request = db.Column(db.String(384), nullable=True, default=None)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def set_status(self, status):
        self.status = status
        if status == data.CONFIRMED:
            self.payment_required = True


class Notification(db.Model):
    __tablename__ = 'notifications'
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
            return 'automated message'
        else:
            return 'from: {}'.format(self.sender)
