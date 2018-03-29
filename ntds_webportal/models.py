from ntds_webportal import db, login
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt
from ntds_webportal.data import ACCESS, NO


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
        return self.access == ACCESS['admin']

    def is_organizer(self):
        return self.access == ACCESS['organizer']

    def is_tc(self):
        return self.access == ACCESS['team_captain']

    def is_treasurer(self):
        return self.access == ACCESS['treasurer']

    def is_bdo(self):
        return self.access == ACCESS['blind_date_organizer']

    def allowed(self, access_level):
        return self.access <= access_level

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.user_id, 'exp': time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

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
    contestant_info = db.relationship('ContestantInfo', backref='contestant', cascade='all, delete-orphan')
    dancing_info = db.relationship('DancingInfo', backref='contestant', cascade='all, delete-orphan')
    volunteer_info = db.relationship('VolunteerInfo', backref='contestant', cascade='all, delete-orphan')
    additional_info = db.relationship('AdditionalInfo', backref='contestant', cascade='all, delete-orphan')
    status_info = db.relationship('StatusInfo', backref='contestant', cascade='all, delete-orphan')

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
    number = db.Column(db.Integer, nullable=False)
    team_captain = db.Column(db.Boolean, nullable=False, default=False)
    student = db.Column(db.Boolean, index=True, nullable=False)
    diet_allergies = db.Column('Diet/Allergies', db.String(512), nullable=True, default=None)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)
    team = db.relationship('Team')

    def __repr__(self):
        return '{id}: {name}'.format(id=self.number, name=self.contestant)


class DancingInfo(db.Model):
    __tablename__ = 'dancing_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    ballroom_level = db.Column(db.String(128), nullable=False)
    ballroom_role = db.Column(db.String(128), nullable=False)
    ballroom_blind_date = db.Column(db.Boolean, nullable=False, default=False)
    ballroom_partner = db.Column(db.Integer)
    latin_level = db.Column(db.String(128), nullable=False)
    latin_role = db.Column(db.String(128), nullable=False)
    latin_blind_date = db.Column(db.Boolean, nullable=False, default=False)
    latin_partner = db.Column(db.Integer)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def not_dancing_ballroom(self):
        self.ballroom_level = NO
        self.ballroom_role = NO
        self.ballroom_blind_date = False
        self.ballroom_partner = None

    def not_dancing_latin(self):
        self.latin_level = NO
        self.latin_role = NO
        self.latin_blind_date = False
        self.latin_partner = None


class VolunteerInfo(db.Model):
    __tablename__ = 'volunteer_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    volunteer = db.Column(db.String(8), nullable=False)
    first_aid = db.Column(db.String(8), nullable=False)
    jury_ballroom = db.Column(db.String(8), nullable=False)
    jury_latin = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)

    def not_volunteering(self):
        self.volunteer = NO
        self.first_aid = NO
        self.jury_ballroom = NO
        self.jury_latin = NO


class AdditionalInfo(db.Model):
    __tablename__ = 'additional_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    sleeping_arrangements = db.Column(db.Boolean, nullable=False)
    t_shirt = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)


class StatusInfo(db.Model):
    __tablename__ = 'status_info'
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestants.contestant_id'), primary_key=True)
    status = db.Column(db.String(8), index=True, default=None)
    paid = db.Column(db.Boolean, index=True, nullable=False, default=False)

    def __repr__(self):
        return '{name}'.format(name=self.contestant)
