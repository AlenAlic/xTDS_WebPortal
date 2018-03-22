from ntds_webportal import db, login
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


ACCESS = {
    'admin': 0,
    'organizer': 1,
    'team_captain': 2,
    'treasurer': 3,
    'blind_date_organizer': 4
}


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128), index=True)
    access = db.Column(db.Integer, index=True)
    is_active = db.Column(db.Boolean, index=True, default=False)
    team = db.relationship('Team')
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))

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
        return self.access == ACCESS['treasurer']

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
    city = db.Column(db.String(128))
    name = db.Column(db.String(128))

    def __repr__(self):
        return '{}'.format(self.city)


class Contestant(db.Model):
    __tablename__ = 'contestants'
    contestant_id = db.Column(db.Integer, primary_key=True)
