from ntds_webportal import db
from ntds_webportal.models import Contestant, ContestantInfo
from ntds_webportal.tournament_config import *


def rearrange_numbers():
    all_dancers = db.session.query(Contestant).join(ContestantInfo)\
        .order_by(ContestantInfo.team_id, Contestant.contestant_id).all()
    all_teams = list(set([dancer.contestant_info[0].team_id for dancer in all_dancers]))
    all_teams.sort()
    max_number = 0
    for team_id in all_teams:
        all_team_dancers = [dancer for dancer in all_dancers if dancer.contestant_info[0].team_id == team_id]
        if max_number > 0:
            for dancer in all_team_dancers:
                dancer.contestant_info[0].number += max_number
                if dancer.dancing_info[0].ballroom_partner is not None:
                    dancer.dancing_info[0].ballroom_partner += max_number
                if dancer.dancing_info[0].latin_partner is not None:
                    dancer.dancing_info[0].latin_partner += max_number
        max_number = max([dancer.contestant_info[0].number for dancer in all_dancers if dancer.contestant_info[0].team_id == team_id])
    db.session.commit()


class DancingGroup:
    measure = {LEAD: 1, FOLLOW: -1}

    def __init__(self):
        self.group = {BALLROOM: {cat: 0 for cat in PARTICIPATING_LEVELS}, LATIN: {cat: 0 for cat in PARTICIPATING_LEVELS}}

    def set_dancer(self, dancer):
        self.group[BALLROOM][dancer.dancing_info[0].ballroom_level] += self.measure[dancer.dancing_info[0].ballroom_role]
        self.group[LATIN][dancer.dancing_info[0].latin_level] += self.measure[dancer.dancing_info[0].latin_role]

    def update_group(self, partners):
        for partner in partners[BALLROOM]:
            self.group[BALLROOM][partner.dancing_info[0].ballroom_level] += self.measure[partner.dancing_info[0].ballroom_role]
        for partner in partners[LATIN]:
            self.group[LATIN][partner.dancing_info[0].latin_level] += self.measure[partner.dancing_info[0].latin_role]

    def check_complete(self):
        missing_combos = {BALLROOM: [k for k, v in self.group[BALLROOM].items() if v != 0],
                          LATIN: [k for k, v in self.group[LATIN].items() if v != 0]}
        return True
            

def find_partners(dancers_list, dancer, team=None):
    """Finds the/a partner for a dancer"""
    group = DancingGroup()
    group.set_dancer(dancer)
    partners = {BALLROOM: [], LATIN: []}
    dancer_team = dancer.contestant_info[0].team_id
    dancer_ballroom_partner = dancer.dancing_info[0].ballroom_partner
    dancer_latin_partner = dancer.dancing_info[0].latin_partner
    if dancer_ballroom_partner == dancer_latin_partner and dancer_ballroom_partner is not None:
        partners[BALLROOM].append(next((d for d in dancers_list if d.dancing_info[0].ballroom_partner == dancer.contestant_info[0].number)))
        partners[LATIN].append(next((d for d in dancers_list if d.dancing_info[0].latin_partner == dancer.contestant_info[0].number)))
    if dancer_ballroom_partner is not None and dancer_latin_partner is None:
        partners[BALLROOM].append(next((d for d in dancers_list if d.dancing_info[0].ballroom_partner == dancer.contestant_info[0].number)))
    if dancer_ballroom_partner is None and dancer_latin_partner is not None:
        partners[LATIN].append(next((d for d in dancers_list if d.dancing_info[0].latin_partner == dancer.contestant_info[0].number)))
    group.update_group(partners)
    if group.check_complete():
        return True
    else:
        return False


def test_func():
    find_partners(db.session.query(Contestant).join(ContestantInfo).filter(ContestantInfo.team_id == 1).all(),
                  db.session.query(Contestant).filter(Contestant.first_name == 'Merel').first())
