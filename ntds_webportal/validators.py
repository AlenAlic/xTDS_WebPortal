# noinspection PyProtectedMember
from wtforms.validators import ValidationError
from ntds_webportal import db
from ntds_webportal.models import Contestant, User
from ntds_webportal.data import LEAD, FOLLOW, CHOOSE, NO, NONE

REQUIRED = 'This field is required.'
SAME_ROLE = 'You can not dance as a {role} with that partner, the selected partner already is a {role}. ' \
            'Please select a different role or a different partner.'
NO_LEVEL = 'The selected partner is not dancing in this category.'
DIFFERENT_LEVELS = 'You can not dance in the chosen level, the selected partner is dancing in a different level. ' \
                   'Please select a different level or a different partner.'
MUST_BLIND_DATE = 'You cannot have a partner at this level.'


class Level(object):
    """Checks if a dancing level is selected."""
    def __call__(self, form, field):
        if field.data == CHOOSE:
            raise ValidationError(field.gettext('Please choose a level to dance at for this category.'))
        if field.data == 'diff_levels_no_level':
            raise ValidationError(field.gettext(NO_LEVEL))
        if field.data == 'diff_levels':
            raise ValidationError(field.gettext(DIFFERENT_LEVELS.format(lvl=field.description)))
        if field.data == 'must_blind_date':
            raise ValidationError(field.gettext(MUST_BLIND_DATE))


class Role(object):
    """Validates if the chosen role is valid."""
    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, form, field):
        try:
            other = form[self.field_name]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.field_name)
        if field.data == NONE and other.data == CHOOSE:
            raise ValidationError(
                field.gettext('Please select a role or indicate that you are not dancing for this category.'))
        if other.data != CHOOSE and other.data != NO:
            if field.data == NONE:
                raise ValidationError(field.gettext('Please select a role to dance as for this category.'))
            if field.data == 'same_role_lead':
                raise ValidationError(field.gettext(SAME_ROLE.format(role=LEAD)))
            if field.data == 'same_role_follow':
                raise ValidationError(field.gettext(SAME_ROLE.format(role=FOLLOW)))


class ChoiceMade(object):
    """Checks if a choice is selected from a list."""
    def __call__(self, form, field):
        if field.data == CHOOSE or field.data == NONE:
            raise ValidationError(field.gettext(REQUIRED))


class IsBoolean(object):
    """Checks if the value is a Boolean."""
    def __call__(self, form, field):
        if not (field.data == str(True) or field.data == str(False)):
            raise ValidationError(field.gettext(REQUIRED))


class SpecificVolunteer(object):
    """Checks if the volunteering fields are valid."""
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data == NONE and other.data != NO:
            raise ValidationError(
                field.gettext(REQUIRED))


class UniqueEmail(object):
    """Checks if an e-mail address is unique."""
    def __call__(self, form, field):
        email_list = [i[0] for i in db.session.query(Contestant.email).all()]
        email_list = [mail.lower() for mail in email_list]
        if field.data.lower() in email_list:
            raise ValidationError(field.gettext('This e-mail address is already in use.'))


class UniqueUsername(object):
    """Checks if an username is unique."""
    def __call__(self, form, field):
        username_list = [i[0] for i in db.session.query(User.username).all()]
        if field.data in username_list:
            raise ValidationError(field.gettext('This username already exists.'))
