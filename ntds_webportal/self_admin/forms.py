from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
from ntds_webportal.data import *
from ntds_webportal.validators import UniqueEmail, UniqueUsername
from wtforms_sqlalchemy.fields import QuerySelectField
import wtforms_sqlalchemy.fields as f


def get_pk_from_identity(obj):
    cls, key = f.identity_key(instance=obj)[:2]
    return ':'.join(f.text_type(x) for x in key)


f.get_pk_from_identity = get_pk_from_identity


class SwitchUserForm(FlaskForm):
    user = SelectField(label='User', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Switch to user')


class CreateBaseUserWithoutEmailForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), UniqueUsername()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('repeat_password', message='Passwords must match.')])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired()])


class CreateBaseUserWithEmailForm(CreateBaseUserWithoutEmailForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(), UniqueEmail()])


class CreateOrganizerForm(CreateBaseUserWithEmailForm):
    send_email = SelectField('Send e-mail upon receiving new message?', choices=[(k, v) for k, v in YN.items()])


class EditOrganizerForm(CreateOrganizerForm):
    password = PasswordField('Password', validators=[EqualTo('repeat_password', message='Passwords must match.')])
    repeat_password = PasswordField('Repeat Password')


class EditAssistantAccountForm(CreateBaseUserWithoutEmailForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[EqualTo('repeat_password', message='Passwords must match.')])
    repeat_password = PasswordField('Repeat Password')


class CreateTeamCaptainAccountForm(CreateBaseUserWithEmailForm):
    team = QuerySelectField("Team", validators=[DataRequired()], allow_blank=False)


class CreateTeamForm(FlaskForm):
    name = StringField('Team name')
    city = StringField('Team city')
    country = SelectField('Country', choices=[(c, c) for c in COUNTRIES])
