from flask_wtf import FlaskForm
from wtforms import TextAreaField


class FeedbackForm(FlaskForm):
    feedback = TextAreaField('', render_kw={"style": "resize:none", "rows": "4", "maxlength": "512"})
