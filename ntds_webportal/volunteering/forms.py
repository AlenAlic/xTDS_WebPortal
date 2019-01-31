from flask import g, request
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DateTimeField, IntegerField, TimeField
from wtforms.validators import DataRequired, Email, NumberRange
from ntds_webportal.data import *
from ntds_webportal.validators import IsBoolean
from ntds_webportal.teamcaptains.forms import VolunteerForm
from datetime import datetime
from ntds_webportal.models import Team, User, Contestant, StatusInfo, ContestantInfo, ShiftInfo


class SuperVolunteerForm(VolunteerForm):
    first_name = StringField('First name', validators=[DataRequired()])
    prefixes = StringField('Prefix')
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    diet_allergies = StringField('Diet/Allergies')
    sleeping_arrangements = SelectField('Sleeping spot', validators=[IsBoolean()],
                                        choices=[(k, v) for k, v in SLEEPING.items()])
    remark = TextAreaField('Remarks', render_kw={"style": "resize:none", "rows": "4", "maxlength": "512"})

    def custom_validate(self):
        if self.jury_ballroom.data == NO:
            self.level_jury_ballroom.data = BELOW_D
            self.license_jury_ballroom.data = NO
        if self.jury_latin.data == NO:
            self.level_jury_latin.data = BELOW_D
            self.license_jury_latin.data = NO
    
    def populate(self, super_volunteer):
        self.first_name.data = super_volunteer.first_name
        self.prefixes.data = super_volunteer.prefixes
        self.last_name.data = super_volunteer.last_name
        self.email.data = super_volunteer.email
        self.sleeping_arrangements.data = str(super_volunteer.sleeping_arrangements)
        self.diet_allergies.data = super_volunteer.diet_allergies
        self.first_aid.data = str(super_volunteer.first_aid)
        self.emergency_response_officer.data = str(super_volunteer.emergency_response_officer)
        self.jury_ballroom.data = super_volunteer.jury_ballroom
        self.jury_latin.data = super_volunteer.jury_latin
        self.license_jury_ballroom.data = super_volunteer.license_jury_ballroom
        self.license_jury_latin.data = super_volunteer.license_jury_latin
        self.level_jury_ballroom.data = super_volunteer.level_ballroom
        self.level_jury_latin.data = super_volunteer.level_latin
        self.jury_salsa.data = super_volunteer.jury_salsa
        self.jury_polka.data = super_volunteer.jury_polka
        self.remark.data = super_volunteer.remark


class ShiftTypeForm(FlaskForm):
    name = StringField('Type name', validators=[DataRequired()])
    coordinator = StringField('Coordinator')
    location = StringField('Location')
    description = TextAreaField('Description', render_kw={"rows": "10"})
    submit = SubmitField('Create task')

    def populate(self, shift_info):
        self.name.data = shift_info.name
        self.coordinator.data = shift_info.coordinator
        self.location.data = shift_info.location
        self.description.data = shift_info.description


class ShiftForm(FlaskForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team.choices = [(0, '')] + \
                            [(t.team_id, t) for t in Team.query.filter(Team.name == TEAM_ORGANIZATION).all()] + \
                            [(t.team_id, t) for t in Team.query.filter(Team.name == TEAM_SUPER_VOLUNTEER).all()] + \
                            [(t.team_id, t) for t in Team.query.filter(Team.name != TEAM_SUPER_VOLUNTEER).all()
                             if t.is_active()]
        self.type.choices = [(0, '')] + [(s.shift_info_id, s.name) for s in
                                         ShiftInfo.query.order_by(ShiftInfo.name).all()]
        start = datetime.fromtimestamp(g.sc.tournament_starting_date)
        default_start = datetime(year=start.year, month=start.month, day=start.day, hour=9, minute=0, second=0)
        default_stop = default_start.replace(hour=10)
        self.start_time.default = default_start
        self.stop_time.default = default_stop
        if request.method == 'GET':
            self.start_time.data = default_start
            self.stop_time.data = default_stop

    type = SelectField('Task', coerce=int, validators=[NumberRange(min=1, message='This field is required.')])
    start_time = DateTimeField("Starting time", validators=[DataRequired()],
                               render_kw={"type": "datetime", "max": "2099-12-30", "min": "2018-01-30"})
    stop_time = DateTimeField("End of shift", validators=[DataRequired()],
                              render_kw={"type": "datetime", "max": "2099-12-30", "min": "2018-01-30"})
    duration = TimeField('Duration', validators=[DataRequired()],
                         default=datetime.now().replace(hour=1, minute=0, second=0, microsecond=0))
    repeats = IntegerField('Repeats', validators=[NumberRange(min=1)], default=1,
                           description="Number of times this shift will be created, each starting after the "
                                       "previous has ended.")
    slots = IntegerField('Number of volunteers needed', validators=[DataRequired(), NumberRange(min=1)],
                         description="This will create an 'x' amount of slots for the shift, with each slot "
                                     "corresponding to one volunteer.")
    team = SelectField('Team', coerce=int, render_kw={'data-role': 'select2'},
                       description="Assigning a team will assign each of the slots that get created to that team.")
    mandatory = SelectField('Mandatory', validators=[IsBoolean()], choices=[('', '')] + [(k, v) for k, v in YN.items()],
                            description="Making a slot mandatory, will not allow the assigned team to give that slot "
                                        "away to a different team.")
    submit = SubmitField('Create Shift')

    def populate(self, shift):
        self.type.data = shift.info_id
        self.start_time.data = shift.start_time
        self.stop_time.data = shift.stop_time
        self.slots.data = shift.max_slots()
        for slot in shift.slots:
            if slot.mandatory:
                self.mandatory.data = str(True)
                break
        else:
            self.mandatory.data = str(False)


class ShiftSlotForm(FlaskForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team.choices = [(0, '')] + \
                            [(t.team_id, t) for t in Team.query.filter(Team.name == TEAM_ORGANIZATION).all()] + \
                            [(t.team_id, t) for t in Team.query.filter(Team.name == TEAM_SUPER_VOLUNTEER).all()] + \
                            [(t.team_id, t) for t in Team.query.filter(Team.name != TEAM_SUPER_VOLUNTEER).all()
                             if t.is_active()]
        self.volunteer.choices = [(0, 'Please select a volunteer to assign to this shift.')]
        if current_user.is_organizer():
            super_volunteers = User.query.filter(User.volunteer_id.isnot(None)).all()
            contestants = Contestant.query.join(StatusInfo).filter(StatusInfo.status == CONFIRMED).all()
            volunteers = sorted(super_volunteers + [c.user for c in contestants], key=lambda x: x.get_full_name())
            self.volunteer.choices.extend([(u.user_id, f"{u.get_full_name()}") for u in volunteers])
        elif current_user.is_tc():
            volunteers = Contestant.query.join(StatusInfo, ContestantInfo)\
                .filter(ContestantInfo.team == current_user.team, StatusInfo.status == CONFIRMED)\
                .order_by(Contestant.first_name).all()
            self.volunteer.choices.extend([(v.user.user_id, v.user.get_full_name()) for v in volunteers])

    volunteer = SelectField(coerce=int, render_kw={'data-role': 'select2'})
    team = SelectField('Team', coerce=int, render_kw={'data-role': 'select2'}, default=0,
                       description="Warning! Changing the team will drop the volunteer if it is not his/her team.")
    mandatory = SelectField('Mandatory', validators=[IsBoolean()], choices=[('', '')] + [(k, v) for k, v in YN.items()],
                            description="Making a slot mandatory, will not allow the assigned team to give that slot "
                                        "away to a different team.")
    submit = SubmitField('Save')

    def populate(self, slot):
        self.volunteer.data = slot.user_id
        self.team.data = slot.team_id
        self.mandatory.data = str(slot.mandatory)
