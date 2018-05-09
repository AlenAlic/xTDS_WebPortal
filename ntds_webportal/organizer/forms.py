from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField


class NameChangeResponse(FlaskForm):
    remark = TextAreaField(label='remark')
    accept = SubmitField(label='Accept')
    reject = SubmitField(label='Reject')

