from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired


class FeedbackForm(FlaskForm):
    feedback = TextAreaField('', validators=[DataRequired()], render_kw={"style": "resize:none", "rows": "4", "maxlength": "512"})
