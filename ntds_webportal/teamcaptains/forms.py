from flask import g
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, NumberRange
from ntds_webportal.data import *
from ntds_webportal.validators import Level, Role, ChoiceMade, SpecificVolunteer, UniqueEmail, IsBoolean
from wtforms_sqlalchemy.fields import QuerySelectField
import wtforms_sqlalchemy.fields as f


def get_pk_from_identity(obj):
    cls, key = f.identity_key(instance=obj)[:2]
    return ':'.join(f.text_type(x) for x in key)


f.get_pk_from_identity = get_pk_from_identity


PARTNER_TEXT = 'No partner / Partner has not signed up yet'


class DancingInfoForm(FlaskForm):
    ballroom_level = SelectField('Level', validators=[Level()], choices=[(k, v) for k, v in LEVELS.items()])
    ballroom_role = SelectField('Role', validators=[Role('ballroom_level')],
                                choices=[(k, v) for k, v in ROLES.items()])
    ballroom_blind_date = BooleanField('Mandatory blind date', description='I am obliged to blind date',
                                       render_kw={'onclick': "dancingBDGreyOut(id, 'ballroom_partner')"})
    ballroom_partner = QuerySelectField(f"Ballroom partner for {tournament_settings['tournament']}",
                                        validators=[Role('ballroom_level'), Level()],
                                        allow_blank=True, blank_text=PARTNER_TEXT)

    latin_level = SelectField('Level', validators=[Level()], choices=[(k, v) for k, v in LEVELS.items()])
    latin_role = SelectField('Role', validators=[Role('latin_level')], choices=[(k, v) for k, v in ROLES.items()])
    latin_blind_date = BooleanField('Mandatory blind date', description='I am obliged to blind date',
                                    render_kw={'onclick': "dancingBDGreyOut(id, 'latin_partner')"})
    latin_partner = QuerySelectField(f"Latin partner for {tournament_settings['tournament']}",
                                     validators=[Role('latin_level'), Level()],
                                     allow_blank=True, blank_text=PARTNER_TEXT)
    
    def custom_validate(self):
        if self.ballroom_level.data == BEGINNERS:
            self.ballroom_blind_date.data = str(False)
        if self.ballroom_level.data == CLOSED or self.ballroom_level.data == OPEN_CLASS:
            self.ballroom_blind_date.data = str(True)
        if self.latin_level.data == BEGINNERS:
            self.latin_blind_date.data = str(False)
        if self.latin_level.data == CLOSED or self.latin_level.data == OPEN_CLASS:
            self.latin_blind_date.data = str(True)
        if self.ballroom_level.data == NO:
            self.ballroom_role.data = NO
            self.ballroom_blind_date.data = str(False)
            self.ballroom_partner.data = None
        if self.latin_level.data == NO:
            self.latin_role.data = NO
            self.latin_blind_date.data = str(False)
            self.latin_partner.data = None


class BaseContestantForm(DancingInfoForm):
    number = IntegerField('Contestant number', validators=[DataRequired()], render_kw={'disabled': True})
    team = StringField('Team', validators=[DataRequired()], render_kw={'disabled': True})

    # ballroom_level = SelectField('Level', validators=[Level()], choices=[(k, v) for k, v in LEVELS.items()])
    # ballroom_role = SelectField('Role', validators=[Role('ballroom_level')],
    #                             choices=[(k, v) for k, v in ROLES.items()])
    # ballroom_blind_date = BooleanField('Mandatory blind date', description='I am obliged to blind date',
    #                                    render_kw={'onclick': "dancingBDGreyOut(id, 'ballroom_partner')"})
    # ballroom_partner = QuerySelectField(f"Ballroom partner for {tournament_settings['tournament']}",
    #                                     validators=[Role('ballroom_level'), Level()],
    #                                     allow_blank=True, blank_text=PARTNER_TEXT)
    #
    # latin_level = SelectField('Level', validators=[Level()], choices=[(k, v) for k, v in LEVELS.items()])
    # latin_role = SelectField('Role', validators=[Role('latin_level')], choices=[(k, v) for k, v in ROLES.items()])
    # latin_blind_date = BooleanField('Mandatory blind date', description='I am obliged to blind date',
    #                                 render_kw={'onclick': "dancingBDGreyOut(id, 'latin_partner')"})
    # latin_partner = QuerySelectField(f"Latin partner for {tournament_settings['tournament']}",
    #                                  validators=[Role('latin_level'), Level()],
    #                                  allow_blank=True, blank_text=PARTNER_TEXT)

    volunteer = SelectField('Volunteer', validators=[ChoiceMade()], choices=[(k, v) for k, v in VOLUNTEER.items()])
    first_aid = SelectField('First Aid', validators=[SpecificVolunteer('volunteer')],
                            choices=[(k, v) for k, v in FIRST_AID.items()])
    jury_ballroom = SelectField('Adjudicator Ballroom', validators=[SpecificVolunteer('volunteer'), ChoiceMade()],
                                choices=[(k, v) for k, v in JURY_BALLROOM.items()])
    jury_latin = SelectField('Adjudicator Latin', validators=[SpecificVolunteer('volunteer'), ChoiceMade()],
                             choices=[(k, v) for k, v in JURY_LATIN.items()])
    license_jury_ballroom = SelectField('License Ballroom', validators=[DataRequired()],
                                        choices=[(k, v) for k, v in LICENSE_BALLROOM.items()])
    license_jury_latin = SelectField('License Latin', validators=[DataRequired()],
                                     choices=[(k, v) for k, v in LICENSE_LATIN.items()])
    level_jury_ballroom = SelectField('Level Ballroom', validators=[DataRequired()],
                                      choices=[(k, v) for k, v in LEVEL_JURY_BALLROOM.items()])
    level_jury_latin = SelectField('Level Latin', validators=[DataRequired()],
                                   choices=[(k, v) for k, v in LEVEL_JURY_LATIN.items()])
    jury_salsa = SelectField('Adjudicator Salsa', validators=[DataRequired()],
                             choices=[(k, v) for k, v in JURY_SALSA.items()])
    jury_polka = SelectField('Adjudicator Polka', validators=[DataRequired()],
                             choices=[(k, v) for k, v in JURY_POLKA.items()])

    def custom_validate(self):
        if self.jury_ballroom.data == NO:
            self.license_jury_ballroom.data = NO
            self.level_jury_ballroom.data = BELOW_D
        if self.jury_latin.data == NO:
            self.license_jury_latin.data = NO
            self.level_jury_latin.data = BELOW_D

    student = SelectField('Student', validators=[IsBoolean()], choices=[(k, v) for k, v in STUDENT.items()])
    first_time = SelectField('First time', validators=[IsBoolean()],
                             choices=[(k, v) for k, v in FIRST_TIME.items()])
    diet_allergies = StringField('Diet/Allergies')
    sleeping_arrangements = SelectField('Sleeping spot', validators=[IsBoolean()],
                                        choices=[(k, v) for k, v in SLEEPING.items()])
    t_shirt = SelectField('T-shirt - {}'.format(euros(SHIRT_PRICE)), validators=[DataRequired()],
                          choices=[(k, v) for k, v in SHIRTS.items()])


for k, value in MERCHANDISE.items():
    setattr(BaseContestantForm, k, IntegerField(value, validators=[NumberRange(0, 99)], default=0,
                                                render_kw={"type": "number", "min": "0", "max": "99", "step": "1"}))


class RegisterContestantForm(BaseContestantForm):
    first_name = StringField('First name', validators=[DataRequired()])
    prefixes = StringField('Prefix')
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), UniqueEmail()])
    submit = SubmitField('Register')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ballroom_partner.query = Contestant.query.join(ContestantInfo, DancingInfo, StatusInfo) \
            .filter(ContestantInfo.team == current_user.team,
                    or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR),
                    DancingInfo.partner.is_(None), DancingInfo.competition == BALLROOM,
                    or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                        DancingInfo.level == BEGINNERS)).order_by(Contestant.first_name)
        self.latin_partner.query = Contestant.query.join(ContestantInfo, DancingInfo, StatusInfo) \
            .filter(ContestantInfo.team == current_user.team,
                    or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR),
                    DancingInfo.partner.is_(None), DancingInfo.competition == LATIN,
                    or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                        DancingInfo.level == BEGINNERS)).order_by(Contestant.first_name)

    def custom_validate(self):
        super().custom_validate()

    def populate(self, dancer):
        super().populate(dancer)
        self.first_name.data = dancer.first_name
        self.prefixes.data = dancer.prefixes
        self.last_name.data = dancer.last_name
        self.email.data = dancer.email


class EditContestantForm(BaseContestantForm):
    full_name = StringField('Full name', validators=[DataRequired()], render_kw={'disabled': True})
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save changes')

    def __init__(self, dancer, **kwargs):
        super().__init__(**kwargs)
        if dancer.competition(BALLROOM).partner is not None:
            self.ballroom_partner.query = Contestant.query.join(ContestantInfo, DancingInfo, StatusInfo) \
                .filter(or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR),
                        DancingInfo.competition == BALLROOM,
                        or_(and_(ContestantInfo.team != current_user.team, DancingInfo.partner == dancer.contestant_id),
                            and_(ContestantInfo.team == current_user.team, DancingInfo.partner.is_(None),
                                 or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                                     DancingInfo.level == BEGINNERS)))).order_by(Contestant.first_name)
        else:
            self.ballroom_partner.query = Contestant.query.join(ContestantInfo, DancingInfo, StatusInfo) \
                .filter(or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR),
                        DancingInfo.competition == BALLROOM,
                        and_(ContestantInfo.team == current_user.team, DancingInfo.partner.is_(None),
                             or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                                 DancingInfo.level == BEGINNERS))).order_by(Contestant.first_name)
        if dancer.competition(LATIN).partner is not None:
            self.latin_partner.query = Contestant.query.join(ContestantInfo, DancingInfo, StatusInfo) \
                .filter(or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR),
                        DancingInfo.competition == LATIN,
                        or_(and_(ContestantInfo.team != current_user.team, DancingInfo.partner == dancer.contestant_id),
                            and_(ContestantInfo.team == current_user.team, DancingInfo.partner.is_(None),
                                 or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                                     DancingInfo.level == BEGINNERS)))).order_by(Contestant.first_name)
        else:
            self.latin_partner.query = Contestant.query.join(ContestantInfo, DancingInfo, StatusInfo) \
                .filter(or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR),
                        DancingInfo.competition == LATIN,
                        and_(ContestantInfo.team == current_user.team, DancingInfo.partner.is_(None),
                             or_(and_(DancingInfo.level == BREITENSPORT, DancingInfo.blind_date.is_(False)),
                                 DancingInfo.level == BEGINNERS))).order_by(Contestant.first_name)

    def custom_validate(self, dancer):
        if dancer.status_info[0].status == SELECTED or dancer.status_info[0].status == CONFIRMED:
            self.ballroom_level.data = dancer.competition(BALLROOM).level
            self.ballroom_role.data = dancer.competition(BALLROOM).role
            self.ballroom_blind_date.data = dancer.competition(BALLROOM).blind_date
            self.ballroom_partner.data = db.session.query(Contestant).join(ContestantInfo) \
                .filter(Contestant.contestant_id == dancer.competition(BALLROOM).partner).first()
            self.latin_level.data = dancer.competition(LATIN).level
            self.latin_role.data = dancer.competition(LATIN).role
            self.latin_blind_date.data = dancer.competition(LATIN).blind_date
            self.latin_partner.data = db.session.query(Contestant).join(ContestantInfo) \
                .filter(Contestant.contestant_id == dancer.competition(LATIN).partner).first()
        super().custom_validate()
        self.full_name.data = dancer.get_full_name()
    
    def populate(self, dancer):
        super().populate(dancer)
        self.full_name.data = dancer.get_full_name()
        self.email.data = dancer.email


class TeamCaptainForm(FlaskForm):
    number = QuerySelectField('Team captain', allow_blank=True)
    submit = SubmitField('Set team captain')


class CreateCoupleForm(FlaskForm):
    lead = QuerySelectField('Lead', validators=[DataRequired()])
    follow = QuerySelectField('Follow', validators=[DataRequired()])
    competition = SelectField('Competition', validators=[DataRequired()],
                              choices=[(comp, comp) for comp in ALL_COMPETITIONS])
    submit = SubmitField('Create couple')


class PartnerRequestForm(FlaskForm):
    dancer = SelectField(label='My dancer', validators=[DataRequired()], coerce=int)
    other = SelectField(label='Other dancer', validators=[DataRequired()], coerce=int)
    competition = SelectField('Competition', choices=[(comp, comp) for comp in ALL_COMPETITIONS])
    level = SelectField('Level', validators=[Level()],
                        choices=[(k, ALL_LEVELS[k]) for k in PARTICIPATING_LEVELS])
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


class EditDancingInfoForm(DancingInfoForm):
    full_name = StringField('Full name', validators=[DataRequired()], render_kw={'disabled': True})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'disabled': True})
    team = StringField('Team', validators=[DataRequired()], render_kw={'disabled': True})

    submit = SubmitField('Save changes')

    def populate(self, dancer):
        self.ballroom_level.data = dancer.competition(BALLROOM).level
        self.ballroom_role.data = dancer.competition(BALLROOM).role
        self.ballroom_blind_date.data = str(dancer.competition(BALLROOM).blind_date)

        self.latin_level.data = dancer.competition(LATIN).level
        self.latin_role.data = dancer.competition(LATIN).role
        self.latin_blind_date.data = str(dancer.competition(LATIN).blind_date)

    def custom_validate(self):
        if self.ballroom_level.data == BEGINNERS:
            self.ballroom_blind_date.data = str(False)
        if self.ballroom_level.data == CLOSED or self.ballroom_level.data == OPEN_CLASS:
            self.ballroom_blind_date.data = str(True)
        if self.latin_level.data == BEGINNERS:
            self.latin_blind_date.data = str(False)
        if self.latin_level.data == CLOSED or self.latin_level.data == OPEN_CLASS:
            self.latin_blind_date.data = str(True)
        if self.ballroom_level.data == NO:
            self.ballroom_role.data = NO
            self.ballroom_blind_date.data = str(False)
            self.ballroom_partner.data = None
        if self.latin_level.data == NO:
            self.latin_role.data = NO
            self.latin_blind_date.data = str(False)
            self.latin_partner.data = None

        if self.ballroom_blind_date.data == str(True):
            self.ballroom_partner.data = None
        if self.latin_blind_date.data == str(True):
            self.latin_partner.data = None
