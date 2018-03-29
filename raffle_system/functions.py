from ntds_webportal import db
from ntds_webportal.models import Contestant, ContestantInfo
from ntds_webportal.values import *


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


def find_partners(dancers_list, dancer, team=None):
    """Finds the/a partner for a dancer"""
    partners = {BALLROOM: [], LATIN: []}
    dancer_team = dancer.contestant_info[0].team_id
    dancer_ballroom_partner = dancer.dancing_info[0].ballroom_partner
    dancer_latin_partner = dancer.dancing_info[0].latin_partner
    if dancer_ballroom_partner == dancer_latin_partner and dancer_ballroom_partner is not None:
        partners[BALLROOM].append(next((d for d in dancers_list if d.dancing_info[0].ballroom_partner == dancer.contestant_info[0].number)))
        partners[LATIN].append(next((d for d in dancers_list if d.dancing_info[0].latin_partner == dancer.contestant_info[0].number)))
        return partners
    if dancer_ballroom_partner is not None and dancer_latin_partner is None:
        partners[BALLROOM].append(next((d for d in dancers_list if d.dancing_info[0].ballroom_partner == dancer.contestant_info[0].number)))
        return partners
    if dancer_ballroom_partner is None and dancer_latin_partner is not None:
        partners[LATIN].append(next((d for d in dancers_list if d.dancing_info[0].latin_partner == dancer.contestant_info[0].number)))
        return partners
