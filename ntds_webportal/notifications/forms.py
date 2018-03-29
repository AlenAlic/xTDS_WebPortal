from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired


class NotificationForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    body = TextAreaField(label="Message content", validators=[DataRequired()])
    recipients = SelectMultipleField(label="Recipients", validators=[DataRequired()])
    submit = SubmitField('Send message')
