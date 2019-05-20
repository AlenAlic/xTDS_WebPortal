from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from ntds_webportal.models import MerchandiseItem, MerchandiseItemVariant


class FeedbackForm(FlaskForm):
    feedback = TextAreaField('Feedback for team captain (only if there is anything wrong with your submitted data)',
                             validators=[DataRequired()],
                             render_kw={"style": "resize:none", "rows": "4", "maxlength": "512"})


class BuyMerchandiseForm(FlaskForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.merchandise.choices = \
            [(0, "Please select an item")] + \
            [(m.merchandise_item_id, m.display_name()) for m in
             MerchandiseItem.query.order_by(MerchandiseItem.description).all()]
        self.variant.choices = \
            [(0, "Please choose a variant")] + \
            [(m.merchandise_item_variant_id, m.variant_name()) for m in
             MerchandiseItemVariant.query.join(MerchandiseItem).order_by(MerchandiseItem.description,
                                                                         MerchandiseItemVariant.
                                                                         merchandise_item_variant_id).all()]

    merchandise = SelectField("Merchandise", validators=[NumberRange(1, message="Choose an item")], default=0,
                              coerce=int)
    variant = SelectField("Variant", validators=[NumberRange(1, message="Choose a variant of the item")], default=0,
                          coerce=int)
    submit = SubmitField("Order item")
