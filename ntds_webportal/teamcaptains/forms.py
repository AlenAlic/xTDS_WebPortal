from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email
import ntds_webportal.data as data
from ntds_webportal.validators import Level, Role, ChoiceMade, SpecificVolunteer, UniqueEmail, IsBoolean
from wtforms_sqlalchemy.fields import QuerySelectField
import wtforms_sqlalchemy.fields as f


def get_pk_from_identity(obj):
    cls, key = f.identity_key(instance=obj)[:2]
    return ':'.join(f.text_type(x) for x in key)


f.get_pk_from_identity = get_pk_from_identity


class BaseContestantForm(FlaskForm):
    number = IntegerField('Contestant number', validators=[DataRequired()], render_kw={'disabled': True})
    team = StringField('Team', validators=[DataRequired()], render_kw={'disabled': True})

    ballroom_level = SelectField('Level', validators=[Level()], choices=[(k, v) for k, v in data.LEVELS.items()])
    ballroom_role = SelectField('Role', validators=[Role('ballroom_level')],
                                choices=[(k, v) for k, v in data.ROLES.items()])
    ballroom_blind_date = BooleanField('Mandatory blind date',
                                       description='I am obliged to blind date in this category')
    ballroom_partner = QuerySelectField('Ballroom partner', validators=[Role('ballroom_level'), Level()],
                                        allow_blank=True, blank_text='I have no partner in this category')

    latin_level = SelectField('Level', validators=[Level()], choices=[(k, v) for k, v in data.LEVELS.items()])
    latin_role = SelectField('Role', validators=[Role('latin_level')], choices=[(k, v) for k, v in data.ROLES.items()])
    latin_blind_date = BooleanField('Mandatory blind date', description='I am obliged to blind date in this category')
    latin_partner = QuerySelectField('Latin partner', validators=[Role('latin_level'), Level()], allow_blank=True,
                                     blank_text='I have no partner in this category')

    volunteer = SelectField('Volunteer', validators=[ChoiceMade()], choices=[(k, v) for k, v in data.VOLUNTEER.items()])
    first_aid = SelectField('First Aid', validators=[SpecificVolunteer('volunteer')],
                            choices=[(k, v) for k, v in data.FIRST_AID.items()])
    jury_ballroom = SelectField('Adjudicator Ballroom', validators=[SpecificVolunteer('volunteer')],
                                choices=[(k, v) for k, v in data.JURY_BALLROOM.items()])
    jury_latin = SelectField('Adjudicator Latin', validators=[SpecificVolunteer('volunteer')],
                             choices=[(k, v) for k, v in data.JURY_LATIN.items()])
    license_jury_ballroom = SelectField('Adjudicator license Ballroom', validators=[DataRequired()],
                                        choices=[(k, v) for k, v in data.LICENSE_BALLROOM.items()])
    license_jury_latin = SelectField('Adjudicator license Latin', validators=[DataRequired()],
                                     choices=[(k, v) for k, v in data.LICENSE_LATIN.items()])
    jury_salsa = SelectField('Adjudicator Salsa', validators=[DataRequired()],
                              choices=[(k, v) for k, v in data.JURY_SALSA.items()])
    jury_polka = SelectField('Adjudicator Polka', validators=[DataRequired()],
                             choices=[(k, v) for k, v in data.JURY_POLKA.items()])

    # student = BooleanField('Student', description='I am a student')
    # first_time = BooleanField('First time', description='This is my first ETDS')
    student = SelectField('Student', validators=[IsBoolean()], choices=[(k, v) for k, v in data.STUDENT.items()])
    first_time = SelectField('First time', validators=[IsBoolean()],
                             choices=[(k, v) for k, v in data.FIRST_TIME.items()])
    diet_allergies = StringField('Diet/Allergies')
    sleeping_arrangements = SelectField('Sleeping spot', validators=[IsBoolean()],
                                        choices=[(k, v) for k, v in data.SLEEPING.items()])
    # sleeping_arrangements = BooleanField('Sleeping arrangement',
    #                                      description='I would like to make use of the sleeping arrangements')
    t_shirt = SelectField('T-shirt', validators=[DataRequired()], choices=[(k, v) for k, v in data.SHIRTS.items()])


class RegisterContestantForm(BaseContestantForm):
    first_name = StringField('First name', validators=[DataRequired()])
    prefixes = StringField('Prefixes')
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), UniqueEmail()])
    submit = SubmitField('Register')


class EditContestantForm(BaseContestantForm):
    full_name = StringField('Full name', validators=[DataRequired()], render_kw={'disabled': True})
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save changes')


class TeamCaptainForm(FlaskForm):
    number = QuerySelectField('Team captain', allow_blank=True)
    submit = SubmitField('Set team captain')


class PartnerRequestForm(FlaskForm):
    dancer = SelectField(label='My dancer', validators=[DataRequired()], coerce=int)
    other = SelectField(label='Other dancer', validators=[DataRequired()], coerce=int)
    competition = SelectField('Competition', choices=[(data.BALLROOM, data.BALLROOM), (data.LATIN, data.LATIN)])
    level = SelectField('Level', validators=[Level()],
                        choices=[(k, data.ALL_LEVELS[k]) for k in data.PARTICIPATING_LEVELS])
    remark = TextAreaField(label='remark')
    submit = SubmitField('Send partner request')


class PartnerRespondForm(FlaskForm):
    remark = TextAreaField(label='remark')
    accept = SubmitField(label='Accept')
    reject = SubmitField(label='Reject')


class NameChangeRequestForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    prefixes = StringField('Prefixes')
    last_name = StringField('Last name', validators=[DataRequired()])
    submit = SubmitField('Send name change request')
