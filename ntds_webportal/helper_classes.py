from ntds_webportal.models import Contestant, ContestantInfo, StatusInfo, DancingInfo
from ntds_webportal.data import *
from sqlalchemy import or_
from flask_wtf import FlaskForm


TYPE_TRANSLATION = {
    "StringField": "text",
    "SelectField": "select",
    "QuerySelectField": "select",
    "SubmitField": "submit",
    "IntegerField": "text",
    "CSRFTokenField": "hidden",
}


class ReactForm(FlaskForm):

    def field_json(self, field):
        field = getattr(self, field)
        data = {
            "name": field.name,
            "id": field.id,
            "labelFor": field.label.field_id,
            "label": field.label.text,
            "fieldValue": field.data if field.data is not None else field.default,
            "description": field.description if len(field.errors) == 0 else ", ".join(field.errors),
            "error": len(field.errors) > 0,
            "type": TYPE_TRANSLATION[field.type],
            "required": field.flags.required,
            "choices": field.choices if field.type == "SelectField" else [],
        }
        if field.render_kw is not None:
            data.update({
                "placeholder": field.render_kw["placeholder"] if "placeholder" in field.render_kw else "",
                "disabled": field.render_kw["disabled"] if "disabled" in field.render_kw else False,
            })
        return data

    def react(self, field_name=""):
        if field_name == "":
            return {field: self.field_json(field) for field in self.data}
        return self.field_json(field_name)


class TeamPossiblePartners:

    def __init__(self, team_captain, dancer=None, other_teams=False, include_gdpr=False):
        self.team = team_captain.team
        self.dancer = dancer
        self.other_teams = other_teams
        self.include_gdpr = include_gdpr

    def get_dancing_info_list(self, competition, level, role):
        dancers = DancingInfo.query\
            .join(StatusInfo, DancingInfo.contestant_id == StatusInfo.contestant_id)\
            .join(ContestantInfo, DancingInfo.contestant_id == ContestantInfo.contestant_id) \
            .join(Contestant, DancingInfo.contestant_id == Contestant.contestant_id) \
            .order_by(Contestant.first_name)
        if self.include_gdpr:
            dancers = dancers.filter(or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR))
        else:
            dancers = dancers.filter(StatusInfo.status == REGISTERED)
        if not self.other_teams and self.dancer is not None:
            external_partners = dancers.filter(DancingInfo.competition == competition,
                                               DancingInfo.level == level, DancingInfo.role == role,
                                               DancingInfo.partner == self.dancer.contestant_id)\
                .filter(ContestantInfo.team != self.team).all()
        else:
            external_partners = []
        dancers = dancers.filter(DancingInfo.competition == competition, DancingInfo.role == role,
                                 DancingInfo.level == level, DancingInfo.blind_date.is_(False))
        if self.dancer is not None:
            dancers = dancers.filter(or_(DancingInfo.partner.is_(None),
                                         DancingInfo.partner == self.dancer.contestant_id))
        else:
            dancers = dancers.filter(DancingInfo.partner.is_(None))
        if self.other_teams:
            dancers = dancers.filter(ContestantInfo.team != self.team).all()
        else:
            dancers = dancers.filter(ContestantInfo.team == self.team).all()
        return dancers + external_partners

    def ballroom_beginners_leads(self):
        return self.get_dancing_info_list(BALLROOM, BEGINNERS, LEAD)

    def ballroom_beginners_follows(self):
        return self.get_dancing_info_list(BALLROOM, BEGINNERS, FOLLOW)

    def latin_beginners_leads(self):
        return self.get_dancing_info_list(LATIN, BEGINNERS, LEAD)

    def latin_beginners_follows(self):
        return self.get_dancing_info_list(LATIN, BEGINNERS, FOLLOW)

    def ballroom_breitensport_leads(self):
        return self.get_dancing_info_list(BALLROOM, BREITENSPORT, LEAD)

    def ballroom_breitensport_follows(self):
        return self.get_dancing_info_list(BALLROOM, BREITENSPORT, FOLLOW)

    def latin_breitensport_leads(self):
        return self.get_dancing_info_list(LATIN, BREITENSPORT, LEAD)

    def latin_breitensport_follows(self):
        return self.get_dancing_info_list(LATIN, BREITENSPORT, FOLLOW)
    
    @staticmethod
    def choices(dancers, extra_dancers=None):
        if extra_dancers is not None:
            dancers += extra_dancers
        dancers = [(str(dancer.contestant_id), dancer.contestant.get_full_name(),
                    dancer.contestant.contestant_info.team.name) for dancer in dancers]
        if extra_dancers is not None:
            dancers.sort(key=lambda dancer: dancer[1])
        return dancers

    def possible_partners(self):
        return {BALLROOM: {BEGINNERS: {LEAD: self.choices(self.ballroom_beginners_follows()),
                                       FOLLOW: self.choices(self.ballroom_beginners_leads()),
                                       BOTH: self.choices(self.ballroom_beginners_leads(),
                                                          self.ballroom_beginners_follows())
                                       },
                           BREITENSPORT: {LEAD: self.choices(self.ballroom_breitensport_follows()),
                                          FOLLOW: self.choices(self.ballroom_breitensport_leads()),
                                          BOTH: self.choices(self.ballroom_breitensport_leads(),
                                                             self.ballroom_breitensport_follows())
                                          }},
                LATIN: {BEGINNERS: {LEAD: self.choices(self.latin_beginners_follows()),
                                    FOLLOW: self.choices(self.latin_beginners_leads()),
                                    BOTH: self.choices(self.latin_beginners_leads(),
                                                       self.latin_beginners_follows())
                                    },
                        BREITENSPORT: {LEAD: self.choices(self.latin_breitensport_follows()),
                                       FOLLOW: self.choices(self.latin_breitensport_leads()),
                                       BOTH: self.choices(self.latin_breitensport_leads(),
                                                          self.latin_breitensport_follows())
                                       }}
                }
