from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email
from ntds_webportal.data import LEVELS, ROLES, VOLUNTEER, FIRST_AID, JURY_BALLROOM, JURY_LATIN, SHIRTS
from ntds_webportal.validators import Level, Role, Volunteer, SpecificVolunteer, UniqueEmail
from wtforms_sqlalchemy.fields import QuerySelectField
import wtforms_sqlalchemy.fields as f


def get_pk_from_identity(obj):
    cls, key = f.identity_key(instance=obj)[:2]
    return ':'.join(f.text_type(x) for x in key)


f.get_pk_from_identity = get_pk_from_identity


class ContestantForm(FlaskForm):
    number = IntegerField('Contestant number', validators=[DataRequired()], render_kw={'disabled': True})
    first_name = StringField('First name', validators=[DataRequired()])
    prefixes = StringField('Prefixes')
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), UniqueEmail()])
    team = StringField('Team', validators=[DataRequired()], render_kw={'disabled': True})
    team_captain = BooleanField('Team captain', description='I am the team captain')

    ballroom_level = SelectField('Level', validators=[Level()], choices=LEVELS)
    ballroom_role = SelectField('Role', validators=[Role('ballroom_level')], choices=ROLES)
    ballroom_blind_date = BooleanField('Mandatory blind date', description='I am obliged to blind date in this category')
    ballroom_partner = QuerySelectField('Ballroom partner', allow_blank=True)

    latin_level = SelectField('Level', validators=[Level()], choices=LEVELS)
    latin_role = SelectField('Role', validators=[Role('latin_level')], choices=ROLES)
    latin_blind_date = BooleanField('Mandatory blind date', description='I am obliged to blind date in this category')
    latin_partner = QuerySelectField('Latin partner', allow_blank=True)

    volunteer = SelectField('Volunteer', validators=[Volunteer()], choices=VOLUNTEER)
    first_aid = SelectField('First Aid', validators=[SpecificVolunteer('volunteer')], choices=FIRST_AID)
    jury_ballroom = SelectField('Jury Ballroom', validators=[SpecificVolunteer('volunteer')], choices=JURY_BALLROOM)
    jury_latin = SelectField('Jury Latin', validators=[SpecificVolunteer('volunteer')], choices=JURY_LATIN)

    student = BooleanField('Student', description='I am a student')
    diet_allergies = StringField('Diet/Allergies')
    sleeping_arrangement = BooleanField('Sleeping arrangement', description='I would like to make use of the sleeping arrangements')
    t_shirt = SelectField('T-shirt', validators=[DataRequired()], choices=SHIRTS)

    submit = SubmitField('Sign up contestant')
