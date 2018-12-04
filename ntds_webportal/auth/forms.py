from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')


class TreasurerForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = StringField('Personal Message')
    tr_submit = SubmitField('Send e-mail to treasurer')


class SendEmailForNotificationsForm(FlaskForm):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.send_email.label.text = f'Send me an e-mail when I get a new message on this site. ' \
                                     f'(This will be disabled the day of the {g.sc.tournament} starts)'

    send_email = BooleanField()
    email_submit = SubmitField('Save e-mail preference')
