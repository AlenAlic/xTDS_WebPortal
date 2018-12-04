from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired
from ntds_webportal.data import *


class CreateCoupleForm(FlaskForm):
    lead = SelectField('Lead', validators=[DataRequired()], coerce=int, render_kw={'data-role': 'select2'})
    follow = SelectField('Follow', validators=[DataRequired()], coerce=int, render_kw={'data-role': 'select2'})
    competition = SelectField('Competition', validators=[DataRequired()],
                              choices=[(comp, comp) for comp in ALL_COMPETITIONS])
    submit = SubmitField('Create couple')


class CreateCoupleExtraCompetitionForm(FlaskForm):
    lead = SelectField('Lead', validators=[DataRequired()], coerce=int, render_kw={'data-role': 'select2'})
    follow = SelectField('Follow', validators=[DataRequired()], coerce=int, render_kw={'data-role': 'select2'})
    submit = SubmitField('Create couple')
