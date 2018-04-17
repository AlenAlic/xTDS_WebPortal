from wtforms.validators import ValidationError
from ntds_webportal.data import LEAD, FOLLOW
from ntds_webportal import db
from ntds_webportal.models import Contestant

REQUIRED = 'This field is required.'
SAME_ROLE = 'You can not dance as a {role}, the selected partner already has that role. ' \
            'Please select a different role or a different partner.'
NO_LEVEL = 'The selected partner is not dancing in this category.'
DIFFERENT_LEVELS = 'You can not dance in the chosen level, the selected partner is dancing in a different level. ' \
                   'Please select a different level or a different partner.'


class Level(object):
    """
    Checks if a dancing level is selected.
    """
    def __call__(self, form, field):
        if field.data == 'choose':
            raise ValidationError(field.gettext('Please choose a level to dance at for this category.'))
        if field.data == 'diff_levels_no_level':
            raise ValidationError(field.gettext(NO_LEVEL))
        if field.data == 'diff_levels':
            raise ValidationError(field.gettext(DIFFERENT_LEVELS.format(lvl=field.description)))


class Role(object):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    """
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data == 'None' and other.data == 'choose':
            raise ValidationError(
                field.gettext('Please select a role or indicate that you are not dancing for this category.'))
        if other.data != 'choose' and other.data != 'no':
            if field.data == 'None':
                raise ValidationError(field.gettext('Please select a role to dance as for this category.'))
            if field.data == 'same_role_lead':
                raise ValidationError(field.gettext(SAME_ROLE.format(role=LEAD)))
            if field.data == 'same_role_follow':
                raise ValidationError(field.gettext(SAME_ROLE.format(role=FOLLOW)))


class Volunteer(object):
    """
    Checks if a dancing level is selected.
    """
    def __call__(self, form, field):
        if field.data == 'choose':
            raise ValidationError(field.gettext(REQUIRED))


class SpecificVolunteer(object):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    """
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data == 'None' and other.data != 'no':
            raise ValidationError(
                field.gettext(REQUIRED))


class UniqueEmail(object):
    """
    Checks if an e-mail address is unique.
    """
    def __call__(self, form, field):
        email_list = [i[0] for i in db.session.query(Contestant.email).all()]
        if field.data in email_list:
            raise ValidationError(field.gettext('This e-mail address is already in use.'))
