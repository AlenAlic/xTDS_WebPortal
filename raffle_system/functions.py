from ntds_webportal import db
from ntds_webportal.models import Contestant, ContestantInfo, TournamentState
from ntds_webportal.functions import uniquify
from ntds_webportal.data import *
import ast


def export_stats_list():
    with open("stats.txt") as f:
        total = {}
        for line in f:
            d = ast.literal_eval(line)
            if len(total) > 0:
                for k, v in d.items():
                    total[k] += v
            else:
                total = d
    with open('stats_list.txt', 'w', encoding='utf-8') as f1:
        for _, v in total.items():
            f1.write(str(v) + '\n')


def delft_exception(group):
    dancers_list = [True for d in group.dancers if d.contestant_info.team.city == DELFT and
                    (d.dancing_information(BALLROOM).level == BEGINNERS
                     or d.dancing_information(LATIN).level == BEGINNERS)]
    return True in dancers_list


def has_partners(dancer):
    return get_partners_ids(dancer) != []


def get_partners_ids(dancer):
    return [cat.partner for cat in dancer.dancing_info if cat.partner is not None]


def get_combinations(dancer):
    comps = tuple()
    for di in dancer.dancing_info:
        comps += (di.competition, di.level, di.role)
    return comps


def sorted_master_list(ballroom_role, latin_role):
    if ballroom_role == latin_role:
        master_list = [
            [BALLROOM, BEGINNERS, 'ballroom_role', LATIN, BEGINNERS, 'latin_role'],
            [BALLROOM, BEGINNERS, 'ballroom_role', LATIN, NO, NO],
            [BALLROOM, NO, NO, LATIN, BEGINNERS, 'latin_role'],
            [BALLROOM, BEGINNERS, 'ballroom_role', LATIN, BREITENSPORT, 'latin_role'],
            [BALLROOM, BREITENSPORT, 'ballroom_role', LATIN, BEGINNERS, 'latin_role'],
            [BALLROOM, BREITENSPORT, 'ballroom_role', LATIN, BREITENSPORT, 'latin_role'],
            [BALLROOM, BREITENSPORT, 'ballroom_role', LATIN, NO, NO],
            [BALLROOM, NO, NO, LATIN, BREITENSPORT, 'latin_role'],
            [BALLROOM, BREITENSPORT, 'ballroom_role', LATIN, CLOSED, 'latin_role'],
            [BALLROOM, CLOSED, 'ballroom_role', LATIN, BREITENSPORT, 'latin_role'],
            [BALLROOM, BREITENSPORT, 'ballroom_role', LATIN, OPEN_CLASS, 'latin_role'],
            [BALLROOM, OPEN_CLASS, 'ballroom_role', LATIN, BREITENSPORT, 'latin_role'],
            [BALLROOM, CLOSED, 'ballroom_role', LATIN, CLOSED, 'latin_role'],
            [BALLROOM, CLOSED, 'ballroom_role', LATIN, NO, NO],
            [BALLROOM, NO, NO, LATIN, CLOSED, 'latin_role'],
            [BALLROOM, CLOSED, 'ballroom_role', LATIN, OPEN_CLASS, 'latin_role'],
            [BALLROOM, OPEN_CLASS, 'ballroom_role', LATIN, CLOSED, 'latin_role'],
            [BALLROOM, OPEN_CLASS, 'ballroom_role', LATIN, OPEN_CLASS, 'latin_role'],
            [BALLROOM, OPEN_CLASS, 'ballroom_role', LATIN, NO, NO],
            [BALLROOM, NO, NO, LATIN, OPEN_CLASS, 'latin_role'],
        ]
    else:
        master_list = [
            [BALLROOM, BEGINNERS, 'ballroom_role', LATIN, BEGINNERS, 'latin_role'],
            [BALLROOM, BEGINNERS, 'ballroom_role', LATIN, BREITENSPORT, 'latin_role'],
            [BALLROOM, BREITENSPORT, 'ballroom_role', LATIN, BEGINNERS, 'latin_role'],
            [BALLROOM, BREITENSPORT, 'ballroom_role', LATIN, BREITENSPORT, 'latin_role'],
            [BALLROOM, BREITENSPORT, 'ballroom_role', LATIN, CLOSED, 'latin_role'],
            [BALLROOM, CLOSED, 'ballroom_role', LATIN, BREITENSPORT, 'latin_role'],
            [BALLROOM, BREITENSPORT, 'ballroom_role', LATIN, OPEN_CLASS, 'latin_role'],
            [BALLROOM, OPEN_CLASS, 'ballroom_role', LATIN, BREITENSPORT, 'latin_role'],
            [BALLROOM, CLOSED, 'ballroom_role', LATIN, CLOSED, 'latin_role'],
            [BALLROOM, CLOSED, 'ballroom_role', LATIN, OPEN_CLASS, 'latin_role'],
            [BALLROOM, OPEN_CLASS, 'ballroom_role', LATIN, CLOSED, 'latin_role'],
            [BALLROOM, OPEN_CLASS, 'ballroom_role', LATIN, OPEN_CLASS, 'latin_role'],
        ]
    for l in master_list:
        for n, i in enumerate(l):
            if i == 'ballroom_role':
                l[n] = ballroom_role
            if i == 'latin_role':
                l[n] = latin_role
    return [tuple(l) for l in master_list]


def sort_combinations(available_combinations_list):
    available_combinations_list = uniquify(available_combinations_list)
    master_list = [(BALLROOM, NO, NO, LATIN, NO, NO)]
    master_list += sorted_master_list(LEAD, LEAD)
    master_list += sorted_master_list(LEAD, FOLLOW)
    master_list += sorted_master_list(FOLLOW, LEAD)
    master_list += sorted_master_list(FOLLOW, FOLLOW)
    master_list = [l for l in master_list if l in available_combinations_list]
    return master_list


def rearrange_numbers():
    state = TournamentState.query.first()
    if not state.numbers_rearranged:
        all_dancers = db.session.query(Contestant).join(ContestantInfo)\
            .order_by(ContestantInfo.team_id, Contestant.contestant_id).all()
        for i in range(0, len(all_dancers)):
            all_dancers[i].contestant_info.number = i+1
        state.numbers_rearranged = True
        db.session.commit()


def check_combination(dancer, combination):
    dc = []
    for di in dancer.dancing_info:
        dc.extend([di.competition, di.level, di.role])
    return str(tuple(dc)) == combination
