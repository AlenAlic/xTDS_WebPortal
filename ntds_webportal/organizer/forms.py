from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import DataRequired, Email
from ntds_webportal.validators import UniqueEmail


class NameChangeResponse(FlaskForm):
    remark = TextAreaField(label='remark')
    accept = SubmitField(label='Accept')
    reject = SubmitField(label='Reject')


class ChangeEmailForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(), UniqueEmail()])
