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
                di = get_dancing_categories(dancer.dancing_info)
                dancer.contestant_info[0].number += max_number
                for _, cat in di.items():
                    if cat.partner is not None:
                        cat.partner += max_number
        max_number = max([dancer.contestant_info[0].number for dancer in all_dancers if dancer.contestant_info[0].team_id == team_id])
    db.session.commit()


class DancerLists:
    # NO_PARTNER = 'no_partner'

    def __init__(self):
        all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(StatusInfo.status != data.CANCELLED).all()
        self.registered_dancers = [dancer for dancer in all_dancers if dancer.status_info[0].status == data.REGISTERED]
        self.selected_dancers = [dancer for dancer in all_dancers if dancer.status_info[0].status == data.SELECTED]
        self.confirmed_dancers = [dancer for dancer in all_dancers if dancer.status_info[0].status == data.CONFIRMED]
        self.no_partner_list = []
        # self.dancer_lists = {REGISTERED: self.registered_dancers, SELECTED: self.selected_dancers,
        #                      CONFIRMED: self.confirmed_dancers, self.NO_PARTNER: self.no_partner_list}
        self.dancer_lists = {REGISTERED: self.registered_dancers, SELECTED: self.selected_dancers,
                             CONFIRMED: self.confirmed_dancers}

    def list(self, status):
        return self.dancer_lists[status]

    def teamcaptains(self):
        return [dancer for dancer in self.registered_dancers if dancer.contestant_info[0].team_captain]

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

    # def no_partner_found(self, dancer):
    #     self.move_dancer_to_list(dancer, self.NO_PARTNER)

    def add_group(self, group, guaranteed=False):
        if group.check() or guaranteed:
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
        return len(self.selected_dancers) >= (raffle_settings[MAX_DANCERS] - raffle_settings[SELECTION_BUFFER])

    def update_states(self):
        for dancer in self.registered_dancers:
            dancer.status_info[0].set_status(REGISTERED)
        for dancer in self.selected_dancers:
            dancer.status_info[0].set_status(SELECTED)
        for dancer in self.confirmed_dancers:
            dancer.status_info[0].set_status(CONFIRMED)
        # db.session.commit()


class DancingGroup:
    measure = {LEAD: 1, FOLLOW: -1, NO: 0}
    search_criteria = {1: FOLLOW, -1: LEAD, 0: NO}
    profile_criteria = {1: LEAD, -1: FOLLOW, 0: NO}

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
        criteria = {cat: {} for cat in ALL_COMPETITIONS}
        for comp, levels in self.group.items():
            criteria[comp].update({lvl: self.search_criteria[val] for lvl, val in levels.items() if val != 0})
        return criteria

    @staticmethod
    def get_profile(dancer):
        profile = {cat: {} for cat in ALL_COMPETITIONS}
        for di in dancer.dancing_info:
            if di.role != NO:
                profile[di.competition].update({di.level: di.role})
        return profile

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

    def find_dancers(self, criteria, list_of_dancers):
        return [d for d in list_of_dancers if self.get_profile(d) == criteria]
            

def find_partners(dancers_list, dancer, target_team=None):
    """Finds the/a partner for a dancer"""
    print('LFG: {}'.format(dancer.get_full_name()))
    group = DancingGroup()
    group.add(dancer)

    # Check for non-dancing teamcaptains
    if group.check():
        return group

    # Check for a balanced group with partners
    if has_partners(dancer):
        group.add_chain(group.check_chain(dancer, dancers_list), dancers_list)
        if group.check():
            return group

    # Check for 2 man balanced groups by iterating over the remaining dancers in random order
    dancer_team = dancer.contestant_info[0].team
    # dancing_categories = get_dancing_categories(dancer.dancing_info)
    # dancer_ballroom_partner = dancing_categories[BALLROOM].partner
    # dancer_latin_partner = dancing_categories[LATIN].partner
    if target_team is None:
        dancers_list = [d for d in dancers_list if d.contestant_info[0].team != dancer_team]
    else:
        dancers_list = [d for d in dancers_list if d.contestant_info[0].team == target_team]
    dancers_list = [d for d in dancers_list if [di.partner for di in d.dancing_info] == [None, None]]
    random_order_list = list(range(0, len(dancers_list)))
    shuffle(random_order_list)
    for i in random_order_list:
        test_dancer = dancers_list[i]
        verification_group = DancingGroup()
        verification_group.add_group(group)
        verification_group.add(test_dancer)
        if verification_group.check():
            group.add(test_dancer)
            return group

    # Search for 2 man balanced groups (on average slower than random iterations)
    # partner_criteria = group.get_criteria()
    # possible_partners = group.find_dancers(partner_criteria, dancers_list)
    # if len(possible_partners) > 0:
    #     group.add(random.choice(possible_partners))
    #     return group

    return group


