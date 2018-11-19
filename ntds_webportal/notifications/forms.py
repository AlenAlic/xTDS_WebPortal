from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired


class NotificationForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    body = TextAreaField(label="Message content", validators=[DataRequired()],
                         render_kw={"style": "resize:none", "rows": "20", "maxlength": "4096"})
    recipients = SelectMultipleField(label="Recipients", validators=[DataRequired()],
                                     render_kw={'data-role': 'select2'})
    submit = SubmitField('Send message')
