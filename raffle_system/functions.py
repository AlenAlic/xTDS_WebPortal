from raffle_system.raffle_config import *
from ntds_webportal import db
from ntds_webportal.tournament_config import *
from ntds_webportal.functions import get_dancing_categories, get_partners_ids, uniquify, has_partners
from ntds_webportal.models import Contestant, ContestantInfo, StatusInfo, TournamentState
from ntds_webportal.strings import *
import ntds_webportal.data as data
from ntds_webportal.data import REGISTERED, SELECTED, CONFIRMED
import random
from random import shuffle
import itertools


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


class RaffleSystem:
    NO_PARTNER = 'no_partner'
    measure = {LEAD: 1, FOLLOW: -1, NO: 0}

    def __init__(self):
        self.all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(StatusInfo.raffle_status != CANCELLED).order_by(ContestantInfo.team_id, Contestant.first_name).all()
        self.registered_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(StatusInfo.raffle_status == REGISTERED).order_by(ContestantInfo.team_id, Contestant.first_name)\
            .all()
        self.selected_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(StatusInfo.raffle_status == SELECTED).order_by(ContestantInfo.team_id, Contestant.first_name).all()
        self.confirmed_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(StatusInfo.raffle_status == CONFIRMED).order_by(ContestantInfo.team_id, Contestant.first_name).all()
        self.no_partner_list = []
        self.dancer_lists = {REGISTERED: self.registered_dancers, SELECTED: self.selected_dancers,
                             CONFIRMED: self.confirmed_dancers, self.NO_PARTNER: self.no_partner_list}
        state = TournamentState.query.first()
        self.tournament_config = state.get_tournament_config()
        self.raffle_config = state.get_raffle_config()
        self.balance = self.get_balance()

    # def list(self, status):
    #     return self.dancer_lists[status]

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

    def no_partner_found(self, dancer):
        self.move_dancer_to_list(dancer, self.NO_PARTNER)

    def add_group(self, group, guaranteed=False):
        add = False
        if group.check() or guaranteed:
            if not group.check():
                print(TEAMCAPTAIN_EXCEPTION.format(group.dancers[0].get_full_name()))
            else:
                print(string_group_matched(group.dancers))
                add = True
        else:
            # b = self.join_balances(self.balance, group.group)
            # b = self.get_balance_sum(b)
            # if b <= 3:
            #     print(string_group_matched_incomplete(group.dancers))
            #     add = True
            # else:
            print(string_group_no_partner(group.dancers))
        if add:
            # self.update_balance(group)
            for dancer in group.dancers:
                self.select_dancer(dancer)
        else:
            for dancer in group.dancers:
                self.no_partner_found(dancer)

    def complete(self):
        return len(self.selected_dancers) >= (self.raffle_config[MAX_DANCERS] - self.raffle_config[SELECTION_BUFFER])

    def update_states(self):
        for dancer in self.registered_dancers:
            dancer.status_info[0].raffle_status = REGISTERED
        for dancer in self.selected_dancers:
            dancer.status_info[0].raffle_status = SELECTED
        for dancer in self.confirmed_dancers:
            dancer.status_info[0].raffle_status = CONFIRMED
        db.session.commit()

    @staticmethod
    def update_stats(stats, source_list):
        for d in source_list:
            di = get_dancing_categories(d.dancing_info)
            for cat, info in di.items():
                if info.level != NO:
                    stats[info.level][info.competition][info.role] += 1
        for _, cat in stats.items():
            for _, comp in cat.items():
                comp[DIFF] = comp[LEAD] - comp[FOLLOW]
        return stats

    def get_stats(self, status):
        stats = {lvl: {cat: {LEAD: 0, FOLLOW: 0, DIFF: 0} for cat in ALL_COMPETITIONS} for lvl in PARTICIPATING_LEVELS}
        stats = self.update_stats(stats, self.confirmed_dancers)
        if status == SELECTED:
            stats = self.update_stats(stats, self.selected_dancers)
        if status == REGISTERED:
            stats = self.update_stats(stats, self.registered_dancers + self.selected_dancers)
        return stats

    def get_balance(self):
        balance = {comp: {lvl: 0 for lvl in PARTICIPATING_LEVELS + [NO]} for comp in ALL_COMPETITIONS}
        for dancer in self.selected_dancers + self.confirmed_dancers:
            for di in dancer.dancing_info:
                balance[di.competition][di.level] += self.measure[di.role]
        return balance

    def update_balance(self, group):
        for dancer in group.dancers:
            for di in dancer.dancing_info:
                self.balance[di.competition][di.level] += self.measure[di.role]

    @staticmethod
    def join_balances(b1, b2):
        b = {comp: {lvl: 0 for lvl in PARTICIPATING_LEVELS + [NO]} for comp in ALL_COMPETITIONS}
        for comp, levels in b1.items():
            for lvl in levels:
                b[comp][lvl] += b1[comp][lvl]
                b[comp][lvl] += b2[comp][lvl]
        return b

    @staticmethod
    def get_balance_sum(balance):
        s = 0
        for comp, levels in balance.items():
            for lvl in levels:
                s += abs(balance[comp][lvl])
        return s


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

    def add_dancers(self, dancers):
        for dancer in dancers:
            self.add(dancer)

    def add_chain(self, list_of_ids, list_of_dancers):
        chain_dancers = [d for d in list_of_dancers if d.contestant_id in list_of_ids]
        self.add_dancers(chain_dancers)

    def add_group(self, group):
        self.add_dancers(group.dancers)

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

    def get_balance(self):
        balance = {comp: {lvl: 0 for lvl in PARTICIPATING_LEVELS + [NO]} for comp in ALL_COMPETITIONS}
        for dancer in self.dancers:
            for di in dancer.dancing_info:
                balance[di.competition][di.level] += self.measure[di.role]
        return balance

    def get_dancer_types(self):
        combinations = [(c,l,r) for c in ALL_COMPETITIONS for l in PARTICIPATING_LEVELS for r in ALL_ROLES]+[(c,NO,NO) for c in ALL_COMPETITIONS]
        combinations = [(b,l) for b in combinations for l in combinations if b[0] !=l [0]]
        combinations = ''


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

    # Clean up list to not include dancers with at least one partner
    dancer_team = dancer.contestant_info[0].team
    if target_team is None:
        dancers_list = [d for d in dancers_list if d.contestant_info[0].team != dancer_team]
    else:
        dancers_list = [d for d in dancers_list if d.contestant_info[0].team == target_team]
    partner_list = [d for d in dancers_list if [di.partner for di in d.dancing_info] != [None, None]]
    # dancers_list = [d for d in dancers_list if [di.partner for di in d.dancing_info] == [None, None]]

    # See if a balanced group can be formed with 1 or 2 random additional dancers, iterated over in random order
    random_order_list = list(range(0, len(dancers_list)))
    shuffle(random_order_list)
    for i in range(1, 3):
        combinations = list(itertools.combinations(random_order_list, i))
        for comb in combinations:
            verification_group = DancingGroup()
            verification_group.add_group(group)
            for c in comb:
                test_dancer = dancers_list[c]
                if has_partners(test_dancer):
                    verification_group.add_chain(group.check_chain(test_dancer, partner_list), partner_list)
                else:
                    verification_group.add(test_dancer)
            if verification_group.check():
                group.add_group(verification_group)
                return group

    # partner_groups = []
    # for dancer in partner_list:
    #     partners = group.check_chain(dancer, partner_list)
    #     partners.sort()
    #     partners = [d for d in partner_list if d.contestant_id in partners]
    #     if partners not in partner_groups:
    #         partner_groups.append(partners)

    # random_order_list = list(range(0, len(partner_groups)))
    # shuffle(random_order_list)
    # for i in random_order_list:
    #     test_partners = partner_groups[i]
    #     verification_group = DancingGroup()
    #     verification_group.add_group(group)
    #     for p in test_partners:
    #         verification_group.add(p)
    #     if verification_group.check():
    #         for p in test_partners:
    #             group.add(p)
    #         return group


    # random_order_list = list(range(0, len(dancers_list)))
    # shuffle(random_order_list)
    # for i in range(1, 3):
    #     combinations = list(itertools.combinations(random_order_list, i))
    #     for comb in combinations:
    #         verification_group = DancingGroup()
    #         verification_group.add_group(group)
    #         for c in comb:
    #             verification_group.add(dancers_list[c])
    #         if verification_group.check():
    #             group.add_group(verification_group)
    #             return group

    return group


