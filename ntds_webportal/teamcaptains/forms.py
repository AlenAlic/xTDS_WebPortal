from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email
import ntds_webportal.data as data
from ntds_webportal.validators import Level, Role, Volunteer, SpecificVolunteer, UniqueEmail
from wtforms_sqlalchemy.fields import QuerySelectField
import wtforms_sqlalchemy.fields as f


def get_pk_from_identity(obj):
    cls, key = f.identity_key(instance=obj)[:2]
    return ':'.join(f.text_type(x) for x in key)


f.get_pk_from_identity = get_pk_from_identity


class BaseContestantForm(FlaskForm):
    ballroom_level = SelectField('Level', validators=[Level()], choices=[(k, v) for k, v in data.LEVELS.items()])
    ballroom_role = SelectField('Role', validators=[Role('ballroom_level')],
                                choices=[(k, v) for k, v in data.ROLES.items()])
    ballroom_blind_date = BooleanField('Mandatory blind date',
                                       description='I am obliged to blind date in this category')
    ballroom_partner = QuerySelectField('Ballroom partner', allow_blank=True)

    latin_level = SelectField('Level', validators=[Level()], choices=[(k, v) for k, v in data.LEVELS.items()])
    latin_role = SelectField('Role', validators=[Role('latin_level')], choices=[(k, v) for k, v in data.ROLES.items()])
    latin_blind_date = BooleanField('Mandatory blind date', description='I am obliged to blind date in this category')
    latin_partner = QuerySelectField('Latin partner', allow_blank=True)

    volunteer = SelectField('Volunteer', validators=[Volunteer()], choices=[(k, v) for k, v in data.VOLUNTEER.items()])
    first_aid = SelectField('First Aid', validators=[SpecificVolunteer('volunteer')],
                            choices=[(k, v) for k, v in data.FIRST_AID.items()])
    jury_ballroom = SelectField('Jury Ballroom', validators=[SpecificVolunteer('volunteer')],
                                choices=[(k, v) for k, v in data.JURY_BALLROOM.items()])
    jury_latin = SelectField('Jury Latin', validators=[SpecificVolunteer('volunteer')],
                             choices=[(k, v) for k, v in data.JURY_LATIN.items()])

    student = BooleanField('Student', description='I am a student')
    first_time = BooleanField('First time', description='This is my first ETDS')
    diet_allergies = StringField('Diet/Allergies')
    sleeping_arrangements = BooleanField('Sleeping arrangement',
                                         description='I would like to make use of the sleeping arrangements')
    t_shirt = SelectField('T-shirt', validators=[DataRequired()], choices=[(k, v) for k, v in data.SHIRTS.items()])


class RegisterContestantForm(BaseContestantForm):
    number = IntegerField('Contestant number', validators=[DataRequired()], render_kw={'disabled': True})
    first_name = StringField('First name', validators=[DataRequired()])
    prefixes = StringField('Prefixes')
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), UniqueEmail()])
    team = StringField('Team', validators=[DataRequired()], render_kw={'disabled': True})
    submit = SubmitField('Register')


class EditContestantForm(BaseContestantForm):
    full_name = StringField('First name', validators=[DataRequired()], render_kw={'disabled': True})
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save changes')


class TeamCaptainForm(FlaskForm):
    number = QuerySelectField('Team captain', allow_blank=True)
    submit = SubmitField('Set team captain')
