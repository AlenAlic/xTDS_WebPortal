from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField, RadioField, IntegerField, SelectField
from wtforms.validators import Email, DataRequired, NumberRange
from ntds_webportal.validators import UniqueEmail
from ntds_webportal.data import COUNTRIES


class NameChangeResponse(FlaskForm):
    remark = TextAreaField(label='Remarks for the teamcaptain (optional)',
                           render_kw={"style": "resize:none", "rows": "3", "maxlength": "512"})
    accept = SubmitField(label='Accept')
    reject = SubmitField(label='Reject')


class ChangeEmailForm(FlaskForm):
    email = StringField('E-mail', validators=[Email(), UniqueEmail()])


class FinalizeMerchandiseForm(FlaskForm):
    submit = SubmitField('Finalize orders')


class CreateNewMerchandiseForm(FlaskForm):
    item = StringField('Item', validators=[DataRequired()], description="T-shirt, bag, mug, etc.",
                       render_kw={"placeholder": "Merchandise item"})
    price = IntegerField(f"Price", validators=[NumberRange(0)], default=0, description="Price in Eurocents")
    shirt = RadioField('Type of merchandise', choices=[("shirt", "T-shirt"), ("other", "Other")], default="other",
                       description="If a T-shirt is created, sizes will be available from XS to XXL.")
    variants = StringField('Variants', validators=[DataRequired()], render_kw={"placeholder": "Red,Blue,Green,..."},
                           description="A comma separated list of variants of the item (color, size, etc.)")
    new_item_submit = SubmitField('Create item')


class CreateTeamForm(FlaskForm):
    name = StringField('Team name', validators=[DataRequired()])
    city = StringField('Team city', validators=[DataRequired()])
    country = SelectField('Country', choices=[(c, c) for c in COUNTRIES])
