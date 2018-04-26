from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email
import ntds_webportal.data as data
from ntds_webportal.validators import Level, Role, Volunteer, SpecificVolunteer, UniqueEmail
from wtforms_sqlalchemy.fields import QuerySelectField
import wtforms_sqlalchemy.fields as f


class NotificationForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    body = TextAreaField(label="Message content", validators=[DataRequired()])
    recipients = SelectMultipleField(label="Recipients")
    submit = SubmitField('Send message')
