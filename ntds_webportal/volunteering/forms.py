from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email
from ntds_webportal.data import *
from ntds_webportal.validators import IsBoolean
from ntds_webportal.teamcaptains.forms import VolunteerForm


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
