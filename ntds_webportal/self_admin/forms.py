from flask import current_app, request, g
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField, PasswordField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange
from ntds_webportal.data import *
from ntds_webportal.validators import UniqueEmail, UniqueUsername
from wtforms_sqlalchemy.fields import QuerySelectField
import wtforms_sqlalchemy.fields as f
import datetime


def get_pk_from_identity(obj):
    cls, key = f.identity_key(instance=obj)[:2]
    return ':'.join(f.text_type(x) for x in key)


f.get_pk_from_identity = get_pk_from_identity


ASK_LEVEL = 'Will there be a {level} level in the tournament?'
ASK_COMPETITION = 'Will there be a {comp} competition?'
WEB_PAGE_PLACEHOLDER = {"placeholder": "Leave blank if there is no such page"}


class SwitchUserForm(FlaskForm):
    user = SelectField(label='User', validators=[DataRequired()], coerce=int, render_kw={'data-role': 'select2'})
    submit = SubmitField('Switch')


class CreateBaseUserWithoutEmailForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), UniqueUsername()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('repeat_password', message='Passwords must match.')])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired()])


class CreateBaseUserWithEmailForm(CreateBaseUserWithoutEmailForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(), UniqueEmail()])


class CreateOrganizerForm(CreateBaseUserWithEmailForm):
    send_email = SelectField('Send e-mail upon receiving new message?', choices=[(k, v) for k, v in YN.items()])


class EditOrganizerForm(CreateOrganizerForm):
    password = PasswordField('Password', validators=[EqualTo('repeat_password', message='Passwords must match.')])
    repeat_password = PasswordField('Repeat Password')


class EditAssistantAccountForm(CreateBaseUserWithoutEmailForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[EqualTo('repeat_password', message='Passwords must match.')])
    repeat_password = PasswordField('Repeat Password')


class CreateTeamCaptainAccountForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(), UniqueEmail()])
    team = QuerySelectField("Team", validators=[DataRequired()], allow_blank=False)


class CreateTeamForm(FlaskForm):
    name = StringField('Team name')
    city = StringField('Team city')
    country = SelectField('Country', choices=[(c, c) for c in COUNTRIES])


class SystemSetupTournamentForm(FlaskForm):
    tournament = SelectField('What kind of tournament are you hosting?', choices=[(NTDS, NTDS), (ETDS, ETDS)])
    year = SelectField('Year', coerce=int, choices=[(year, year) for year in range(datetime.datetime.now().year,
                                                                                   datetime.datetime.now().year + 5)])
    city = SelectField('City', choices=[(c, c) for c in CITIES])
    tournament_starting_date = DateField("Start date (the Friday)", validators=[DataRequired()],
                                         default=(datetime.datetime.now() + datetime.timedelta(days=120)).date(),
                                         render_kw={"type": "date", "max": "2099-12-30", "min": "2018-01-30"})


class ResetOrganizerAccountForm(SystemSetupTournamentForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.email.default = "testorganizer@xtds.nl" if current_app.config.get('DEBUG') else ""
        if request.method == "GET":
            self.email.data = self.email.default

    username = StringField('Username')
    email = StringField('E-mail', validators=[DataRequired(), Email()])


class SystemSetupForm(SystemSetupTournamentForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_time_ask.label.text = f"Will you ask dancers if this is their first time attending " \
            f"an {g.sc.tournament}?"

    number_of_teamcaptains = IntegerField(f"What is number of team captains that a team can have? "
                                          f"(Remember, team captains are guaranteed entry to the tournament)",
                                          validators=[NumberRange(1, 2)], default=1)

    beginners_level = SelectField(ASK_LEVEL.format(level=BEGINNERS), choices=[(k, v) for k, v in YN.items()])
    closed_level = SelectField(ASK_LEVEL.format(level=CLOSED), choices=[(k, v) for k, v in YN.items()])
    breitensport_obliged_blind_date = SelectField(f"Is there a cutoff where {BREITENSPORT} dancers must Blind Date?",
                                                  choices=[(k, v) for k, v in YN.items()])
    salsa_competition = SelectField(ASK_COMPETITION.format(comp=SALSA), choices=[(k, v) for k, v in YN.items()])
    polka_competition = SelectField(ASK_COMPETITION.format(comp=POLKA), choices=[(k, v) for k, v in YN.items()])

    student_price = IntegerField(f"What is the admission fee price for a {STUDENT}? (in Euro cents)",
                                 validators=[NumberRange(0)], default=DEFAULT_STUDENT_PRICE)
    non_student_price = IntegerField(f"What is the admission fee price for a {NON_STUDENT}? (in Euro cents)",
                                     validators=[NumberRange(0)], default=DEFAULT_NON_STUDENT_PRICE)
    phd_student_category = SelectField(f"Will there be a separate pricing category for PhD students?",
                                       choices=[(k, v) for k, v in YN.items()])
    phd_student_price = IntegerField(f"What is the admission fee price for a {PHD_STUDENT}? (in Euro cents)",
                                     validators=[NumberRange(0)], default=DEFAULT_PHD_STUDENT_PRICE)

    first_time_ask = SelectField("", choices=[(k, v) for k, v in YN.items()])
    ask_adult = SelectField(f"Will you ask dancers if they are at least 18 years old at the time of the tournament?",
                            choices=[(k, v) for k, v in YN.items()])

    ask_diet_allergies = SelectField("Will you ask dancers about their allergies and dietary restrictions?",
                                     choices=[(k, v) for k, v in YN.items()])
    ask_volunteer = SelectField("Will you ask dancers if they want to volunteer in general?",
                                choices=[(k, v) for k, v in YN.items()])
    ask_first_aid = SelectField("Will you ask dancers if they want to volunteer as a First Aid Officer?",
                                choices=[(k, v) for k, v in YN.items()])
    ask_emergency_response_officer = SelectField("Will you ask dancers if they want to volunteer as an Emergency "
                                                 "Response Officer?", choices=[(k, v) for k, v in YN.items()])
    ask_adjudicator_highest_achieved_level = SelectField("Will you ask volunteers that wish to be an adjudicator "
                                                         "what their highest achieved level is?",
                                                         choices=[(k, v) for k, v in YN.items()])
    ask_adjudicator_certification = SelectField("Will you ask volunteers that wish to be an adjudicator "
                                                "if they have a certification to adjudicate?",
                                                choices=[(k, v) for k, v in YN.items()])
    finances_full_refund = SelectField("Will you be giving full refunds to dancers that cancel their registration?",
                                       choices=[(k, v) for k, v in YN.items()])
    finances_partial_refund = SelectField("Will you be giving partial refunds to dancers that cancel their "
                                          "registration?", choices=[(k, v) for k, v in YN.items()])
    finances_partial_refund_percentage = IntegerField(f"What is the refund percentage?",
                                                      validators=[NumberRange(0, 100)], default=50)
    finances_refund_date = DateField("What is the date past which there will not be any more refunds?",
                                     validators=[DataRequired()], default=datetime.datetime.now().date(),
                                     render_kw={"type": "date", "max": "2099-12-30", "min": "2018-01-30"})

    main_page_link = StringField(f"What is the main domain of your website?", render_kw=WEB_PAGE_PLACEHOLDER)
    terms_and_conditions_link = StringField(f"What is the web page that the terms and conditions for the tournament?",
                                            render_kw=WEB_PAGE_PLACEHOLDER)
    merchandise_link = StringField(f"What is the web page that shows the merchandise (if any)?",
                                   render_kw=WEB_PAGE_PLACEHOLDER)


class MerchandiseDateForm(FlaskForm):
    merchandise_closing_date = DateField("What is the last date at which merchandise can be ordered?",
                                         validators=[], default=datetime.datetime.now().date(),
                                         render_kw={"type": "date", "max": "2099-12-30", "min": "2018-01-30"})
    merchandise_closing_submit = SubmitField("Set date")
