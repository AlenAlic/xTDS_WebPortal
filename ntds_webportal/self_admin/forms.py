from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired


class SwitchUserForm(FlaskForm):
    user = SelectField(label='User', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Switch to user')
