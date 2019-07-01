from flask import g
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField
from wtforms.validators import NumberRange
from ntds_webportal import db
from ntds_webportal.functions import str2bool
from ntds_webportal.data import *


LION_LEVEL = "Does the {level} level count for Lion points?"


class RaffleConfigurationForm(FlaskForm):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not g.sc.beginners_level:
            self.beginners_guaranteed_entry_cutoff.data = str(False)
            self.beginners_guaranteed_cutoff.data = 0
            self.beginners_guaranteed_per_team.data = str(False)
            self.beginners_minimum_entry_per_team.data = 0
            self.beginners_increased_chance.data = str(False)
        if not g.sc.first_time_ask:
            self.first_time_guaranteed_entry.data = str(False)
            self.first_time_increased_chance.data = str(False)
        if g.sc.tournament == ETDS:
            self.lions_guaranteed_per_team.data = str(False)
            self.closed_lion.data = str(False)
            self.open_class_lion.data = str(False)
            self.lions_minimum_entry_per_team.data = 0

    maximum_number_of_dancers = IntegerField(f"What is maximum number of dancers that will be let into the tournament?",
                                             validators=[NumberRange(100, 1000)], default=400)
    selection_buffer = IntegerField(f"How much of a buffer should be left at the end of the raffle?",
                                    validators=[NumberRange(0, 1000)], default=40)
    
    beginners_guaranteed_entry_cutoff = SelectField(f"Is there an amount of {BEGINNERS} where, if less than that "
                                                    f"amount have signed up, all beginners will be guaranteed entry "
                                                    f"to the tournament?", choices=[(k, v) for k, v in YN.items()])
    beginners_guaranteed_cutoff = IntegerField(f"What is cutoff for selecting all {BEGINNERS} to the tournament?",
                                               validators=[NumberRange(0, 200)], default=80)
    beginners_guaranteed_per_team = SelectField(f"Will a number of {BEGINNERS} from each team be guaranteed entry "
                                                f"to the tournament?", choices=[(k, v) for k, v in YN.items()])
    beginners_minimum_entry_per_team = IntegerField(f"What is the minimum number of {BEGINNERS} that will be "
                                                    f"guaranteed entry per team?",
                                                    validators=[NumberRange(0, 10)], default=4)
    beginners_increased_chance = SelectField(f"Will {BEGINNERS} be given an increased chance to be selected "
                                             f"for the tournament?", choices=[(k, v) for k, v in YN.items()])

    first_time_guaranteed_entry = SelectField("Will first time attendees be guaranteed entry to the tournament?",
                                              choices=[(k, v) for k, v in YN.items()])
    first_time_increased_chance = SelectField("Will first time attendees be given an increased chance to be selected "
                                              "for the tournament?", choices=[(k, v) for k, v in YN.items()])

    not_selected_last_time_guaranteed_entry = SelectField("Will dancers that have not been selected for the last "
                                                          "tournament be guaranteed entry to the tournament?",
                                                          choices=[(k, v) for k, v in YN.items()])
    not_selected_last_time_increased_chance = SelectField("Will dancers that have not been selected for the last "
                                                          "tournament be given an increased chance to be selected for "
                                                          "the tournament?", choices=[(k, v) for k, v in YN.items()])

    guaranteed_team_size = SelectField(f"Will there be a minimum team size, below which all dancers are granted entry "
                                       f"to the tournament?", choices=[(k, v) for k, v in YN.items()])
    minimum_team_size = IntegerField(f"What is the minimum team size for the tournament?",
                                     validators=[NumberRange(0, 20)], default=10)

    lions_guaranteed_per_team = SelectField(f"Will a number of dancers from each team, that count for Lion points, "
                                            f"be guaranteed entry to the tournament?", 
                                            choices=[(k, v) for k, v in YN.items()])
    closed_lion = SelectField(LION_LEVEL.format(level=CLOSED), choices=[(k, v) for k, v in YN.items()])
    open_class_lion = SelectField(LION_LEVEL.format(level=OPEN_CLASS), choices=[(k, v) for k, v in YN.items()])
    lions_minimum_entry_per_team = IntegerField(f'What is the minimum number of Lion dancers that will be guaranteed '
                                                f'entry per team? (Note: Someone dancing in only one discipline will '
                                                f'count as "half" a dancer)',
                                                validators=[NumberRange(0, 15)], default=9)

    def populate(self):
        self.maximum_number_of_dancers.data = g.rc.maximum_number_of_dancers
        self.selection_buffer.data = g.rc.selection_buffer

        self.beginners_guaranteed_entry_cutoff.data = str(g.rc.beginners_guaranteed_entry_cutoff)
        self.beginners_guaranteed_cutoff.data = g.rc.beginners_guaranteed_cutoff
        self.beginners_guaranteed_per_team.data = str(g.rc.beginners_guaranteed_per_team)
        self.beginners_minimum_entry_per_team.data = g.rc.beginners_minimum_entry_per_team
        self.beginners_increased_chance.data = str(g.rc.beginners_increased_chance)

        self.first_time_guaranteed_entry.data = str(g.rc.first_time_guaranteed_entry)
        self.first_time_increased_chance.data = str(g.rc.first_time_increased_chance)

        self.not_selected_last_time_guaranteed_entry.data = str(g.rc.not_selected_last_time_guaranteed_entry)
        self.not_selected_last_time_increased_chance.data = str(g.rc.not_selected_last_time_increased_chance)

        self.guaranteed_team_size.data = str(g.rc.guaranteed_team_size)
        self.minimum_team_size.data = g.rc.minimum_team_size

        self.lions_guaranteed_per_team.data = str(g.rc.lions_guaranteed_per_team)
        self.closed_lion.data = str(g.rc.closed_lion)
        self.open_class_lion.data = str(g.rc.open_class_lion)
        self.lions_minimum_entry_per_team.data = g.rc.lions_minimum_entry_per_team
    
    def custom_validate(self):
        if g.ts.main_raffle_taken_place:
            self.beginners_guaranteed_entry_cutoff.data = str(g.rc.beginners_guaranteed_entry_cutoff)
            self.beginners_guaranteed_cutoff.data = g.rc.beginners_guaranteed_cutoff
            self.beginners_guaranteed_per_team.data = str(g.rc.beginners_guaranteed_per_team)
            self.beginners_minimum_entry_per_team.data = g.rc.beginners_minimum_entry_per_team
            self.beginners_increased_chance.data = str(g.rc.beginners_increased_chance)

            self.first_time_guaranteed_entry.data = str(g.rc.first_time_guaranteed_entry)
            self.first_time_increased_chance.data = str(g.rc.first_time_increased_chance)

            self.not_selected_last_time_guaranteed_entry.data = str(g.rc.not_selected_last_time_guaranteed_entry)
            self.not_selected_last_time_increased_chance.data = str(g.rc.not_selected_last_time_increased_chance)

            self.guaranteed_team_size.data = str(g.rc.guaranteed_team_size)
            self.minimum_team_size.data = g.rc.minimum_team_size

            self.lions_guaranteed_per_team.data = str(g.rc.lions_guaranteed_per_team)
            self.closed_lion.data = str(g.rc.closed_lion)
            self.open_class_lion.data = str(g.rc.open_class_lion)
            self.lions_minimum_entry_per_team.data = g.rc.lions_minimum_entry_per_team
        if str2bool(self.beginners_guaranteed_entry_cutoff.data):
            self.beginners_guaranteed_per_team.data = str(False)
            self.beginners_minimum_entry_per_team.data = 0
            self.beginners_increased_chance.data = str(False)
        else:
            self.beginners_guaranteed_cutoff.data = 0
        if not str2bool(self.beginners_guaranteed_per_team.data):
            self.beginners_minimum_entry_per_team.data = 0
        else:
            self.beginners_increased_chance.data = str(False)

        if str2bool(self.first_time_guaranteed_entry.data):
            self.first_time_increased_chance.data = str(False)

        if str2bool(self.not_selected_last_time_guaranteed_entry.data):
            self.not_selected_last_time_increased_chance.data = str(False)

        if not str2bool(self.guaranteed_team_size.data):
            self.minimum_team_size.data = 0

        if not str2bool(self.lions_guaranteed_per_team.data):
            self.closed_lion.data = str(False)
            self.open_class_lion.data = str(False)
            self.lions_minimum_entry_per_team.data = 0
    
    def save_settings(self):
        g.rc.maximum_number_of_dancers = self.maximum_number_of_dancers.data
        g.rc.selection_buffer = self.selection_buffer.data

        g.rc.beginners_guaranteed_entry_cutoff = str2bool(self.beginners_guaranteed_entry_cutoff.data)
        g.rc.beginners_guaranteed_cutoff = self.beginners_guaranteed_cutoff.data
        g.rc.beginners_guaranteed_per_team = str2bool(self.beginners_guaranteed_per_team.data)
        g.rc.beginners_minimum_entry_per_team = self.beginners_minimum_entry_per_team.data
        g.rc.beginners_increased_chance = str2bool(self.beginners_increased_chance.data)

        g.rc.first_time_guaranteed_entry = str2bool(self.first_time_guaranteed_entry.data)
        g.rc.first_time_increased_chance = str2bool(self.first_time_increased_chance.data)

        g.rc.not_selected_last_time_guaranteed_entry = str2bool(self.not_selected_last_time_guaranteed_entry.data)
        g.rc.not_selected_last_time_increased_chance = str2bool(self.not_selected_last_time_increased_chance.data)

        g.rc.guaranteed_team_size = str2bool(self.guaranteed_team_size.data)
        g.rc.minimum_team_size = self.minimum_team_size.data

        g.rc.lions_guaranteed_per_team = str2bool(self.lions_guaranteed_per_team.data)
        g.rc.closed_lion = str2bool(self.closed_lion.data)
        g.rc.open_class_lion = str2bool(self.open_class_lion.data)
        g.rc.lions_minimum_entry_per_team = self.lions_minimum_entry_per_team.data
        db.session.commit()
