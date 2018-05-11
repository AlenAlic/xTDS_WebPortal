from raffle_system.raffle_config import *
from ntds_webportal import db
from ntds_webportal.tournament_config import *
from ntds_webportal.functions import get_dancing_categories, get_partners_ids, uniquify, has_partners
from ntds_webportal.models import Contestant, ContestantInfo, StatusInfo
from ntds_webportal.strings import *
import ntds_webportal.data as data
from ntds_webportal.data import REGISTERED, SELECTED, CONFIRMED
from random import shuffle


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


class DancerLists:
    NO_PARTNER = 'no_partner'

    def __init__(self):
        all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(StatusInfo.status != data.CANCELLED).all()
        self.registered_dancers = [dancer for dancer in all_dancers if dancer.status_info[0].status == data.REGISTERED]
        self.selected_dancers = [dancer for dancer in all_dancers if dancer.status_info[0].status == data.SELECTED]
        self.confirmed_dancers = [dancer for dancer in all_dancers if dancer.status_info[0].status == data.CONFIRMED]
        self.no_partner_list = []
        self.dancer_lists = {REGISTERED: self.registered_dancers, SELECTED: self.selected_dancers,
                             CONFIRMED: self.confirmed_dancers, self.NO_PARTNER: self.no_partner_list}

    def list(self, status):
        return self.dancer_lists[status]

    def teamcaptains(self):
        return [dancer for dancer in self.registered_dancers if dancer.contestant_info[0].team_captain is True]

    def check_availability(self, dancer):
        return dancer in self.registered_dancers

    def get_dancer_list(self, dancer):
        for k, l in self.dancer_lists.items():
            if dancer in l:
                return k

    def move_dancer_to_list(self, dancer, list_to):
        list_from = self.get_dancer_list(dancer)
        self.dancer_lists[list_from].remove(dancer)
        self.dancer_lists[list_to].append(dancer)

    def select_dancer(self, dancer):
        self.move_dancer_to_list(dancer, SELECTED)

    def no_partner_found(self, dancer):
        self.move_dancer_to_list(dancer, self.NO_PARTNER)

    def add_group(self, group, teamcaptain=False):
        if group.check() or teamcaptain:
            if not group.check():
                print(TEAMCAPTAIN_EXCEPTION.format(group.dancers[0].get_full_name()))
            else:
                print(string_group_matched(group.dancers))
            for dancer in group.dancers:
                self.select_dancer(dancer)
        else:
            print(string_group_no_partner(group.dancers))
            # for dancer in group.dancers:
            #     self.no_partner_found(dancer)

    def complete(self):
        return len(self.selected_dancers) >= raffle_settings[SELECTION_BUFFER]

    def update_states(self):
        for dancer in self.registered_dancers:
            dancer.status_info[0].set_status(REGISTERED)
        for dancer in self.selected_dancers:
            dancer.status_info[0].set_status(SELECTED)
        for dancer in self.confirmed_dancers:
            dancer.status_info[0].set_status(CONFIRMED)
        db.session.commit()


class DancingGroup:
    measure = {LEAD: 1, FOLLOW: -1, NO: 0}
    search_criteria = {1: FOLLOW, -1: LEAD, 0: NO}

    def __init__(self):
        self.group = {cat: {lvl: 0 for lvl in PARTICIPATING_LEVELS} for cat in ALL_COMPETITIONS}
        for cat, d in self.group.items():
            d.update({NO: 0})
        self.dancers = []

    def add(self, dancer):
        dancing_categories = get_dancing_categories(dancer.dancing_info)
        if dancer not in self.dancers:
            self.dancers.append(dancer)
            for _, di in dancing_categories.items():
                self.group[di.competition][di.level] += self.measure[di.role]

    def add_chain(self, list_of_ids, list_of_dancers):
        chain_dancers = [d for d in list_of_dancers if d.contestant_id in list_of_ids]
        for dancer in chain_dancers:
            self.add(dancer)

    def add_group(self, group):
        for dancer in group.dancers:
            self.add(dancer)

    def check(self):
        balance = []
        for _, groups in self.group.items():
            balance.extend([m for _, m in groups.items()])
        return True if [number for number in balance if number == 0] == balance else False

    def get_criteria(self):
        criteria = []
        for cat, level in self.group.items():
            criteria.append({COMPETITION: cat, LEVEL: [k for k, v in level.items() if v != 0][0],
                             ROLE: self.search_criteria[[v for _, v in level.items() if v != 0][0]]})
        return criteria

    @staticmethod
    def check_chain(dancer, list_of_dancers):
        dancer_ids = [dancer.contestant_id]
        partner_ids = uniquify(get_partners_ids(dancer) + dancer_ids)
        if uniquify(get_partners_ids(dancer)) is not []:
            while dancer_ids != partner_ids:
                partners = [d for d in list_of_dancers if d.contestant_id in partner_ids]
                for partner in partners:
                    dancer_ids.append(partner.contestant_id)
                    dancer_ids.extend(get_partners_ids(partner))
                    partner_ids.append(partner.contestant_id)
                    partner_ids.extend(get_partners_ids(partner))
                dancer_ids = uniquify(dancer_ids)
                partner_ids = uniquify(partner_ids)
            return dancer_ids
        else:
            return []

    # def find_dancer(self, criteria):
    #     matching_dancers = []
    #     temp_group = DancingGroup()
    #     for dancer in self.source_dancers:
    #         dancing_categories = get_dancing_categories(dancer.di)
    #         for cat in dancing_categories:
    #             print('')
    #     print('')
    #     return True


# def get_partner_from_list(dancers_list, dancer, category):
#     return next((d for d in dancers_list if
#                  get_dancing_categories(d.dancing_info)[category].partner == dancer.contestant_id))
            

def find_partners(dancers_list, dancer, target_team=None):
    """Finds the/a partner for a dancer"""
    print('LFG: {}'.format(dancer.get_full_name()))
    group = DancingGroup()
    if has_partners(dancer):
        group.add_chain(group.check_chain(dancer, dancers_list), dancers_list)
        if group.check():
            return group
    group.add(dancer)
    dancer_team = dancer.contestant_info[0].team
    # dancing_categories = get_dancing_categories(dancer.dancing_info)
    # dancer_ballroom_partner = dancing_categories[BALLROOM].partner
    # dancer_latin_partner = dancing_categories[LATIN].partner
    # if dancer_ballroom_partner == dancer_latin_partner and dancer_ballroom_partner is not None:
    #     group.add(get_partner_from_list(dancers_list, dancer, BALLROOM))
    #     group.add(get_partner_from_list(dancers_list, dancer, LATIN))
    # if dancer_ballroom_partner is not None and dancer_latin_partner is None:
    #     group.add(get_partner_from_list(dancers_list, dancer, BALLROOM))
    # if dancer_ballroom_partner is None and dancer_latin_partner is not None:
    #     group.add(get_partner_from_list(dancers_list, dancer, LATIN))
    # if group.check():
    #     return group
    if target_team is None:
        dancers_list = [d for d in dancers_list if d.contestant_info[0].team != dancer_team]
    else:
        dancers_list = [d for d in dancers_list if d.contestant_info[0].team == target_team]
    dancers_list = [d for d in dancers_list if [di.partner for di in d.dancing_info] == [None, None]]
    random_order_list = dancers_list
    shuffle(random_order_list)
    for test_dancer in random_order_list:
        verification_group = DancingGroup()
        verification_group.add_group(group)
        verification_group.add(test_dancer)
        if verification_group.check():
            group.add(test_dancer)
            break
    # TRY COMPLEXER COMBINATIONS
    # partner_criteria = group.get_criteria()
    # partner = group.find_dancer(partner_criteria)
    return group


