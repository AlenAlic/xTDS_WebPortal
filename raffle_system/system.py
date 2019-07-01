from flask import g, flash
from ntds_webportal import db
from ntds_webportal.models import User, Contestant, ContestantInfo, StatusInfo, RaffleConfiguration, Notification, \
    SuperVolunteer, NotSelectedContestant
from ntds_webportal.data import *
import time
from random import shuffle
from raffle_system.dancing_group import DancingGroup
from raffle_system.balance import Balance
from raffle_system.functions import delft_exception, get_combinations, sort_combinations, rearrange_numbers, \
    check_combination, has_partners


GROUP_MATCHED = 'Complete group: {}'
GROUP_MATCHED_INCOMPLETE = 'Incomplete group: {}'
GROUP_NO_PARTNER = 'Incomplete group: {}\n\tTemporarily removing from selection'
TEAMCAPTAIN_EXCEPTION = 'Selected {} alone because he/she is a teamcaptain'
GUARANTEED_EXCEPTION = 'Selected {} alone because he/she is guaranteed entry by the organization'
NO_PARTNER = 'No partner available for: {}\n\tTemporarily removing from selection'
BEGINNER_EXCEPTION = 'Selected {} because he/she is a Beginner'
GROUP_MATCHED_INCOMPLETE_REDUCING_DIFFERENCE = 'Incomplete group: {}\n\tSelected due to difference reduction'
GROUP_MATCHED_INCOMPLETE_TEAM_CAPTAIN_EXCEPTION = 'Incomplete group: {}\n\tSelected due to teamcaptain in group'
GROUP_MATCHED_INCOMPLETE_BEGINNERS_EXCEPTION = 'Incomplete group: {}\n\tSelected due to Beginners exception'
GROUP_MATCHED_INCOMPLETE_GENERAL_EXCEPTION = 'Incomplete group: {}\n\tSelected due to general exception'


def string_group(group, base_string):
    group = [d.get_full_name() for d in group.dancers]
    group = ', '.join(group)
    return base_string.format(group)


def string_group_matched(group):
    return string_group(group, GROUP_MATCHED)


def string_group_matched_incomplete(group):
    return string_group(group, GROUP_MATCHED_INCOMPLETE)


def string_group_no_partner(group):
    return string_group(group, GROUP_NO_PARTNER)


def string_group_matched_incomplete_reducing_difference(group):
    return string_group(group, GROUP_MATCHED_INCOMPLETE_REDUCING_DIFFERENCE)


def string_group_matched_incomplete_team_captain_exception(group):
    return string_group(group, GROUP_MATCHED_INCOMPLETE_TEAM_CAPTAIN_EXCEPTION)


def string_group_guaranteed_exception(group):
    return string_group(group, GROUP_MATCHED_INCOMPLETE_GENERAL_EXCEPTION)


class RaffleSystem(Balance):
    NO_PARTNER = 'no_partner'
    measure = {LEAD: 1, FOLLOW: -1, NO: 0}

    def __init__(self):
        super().__init__()
        self.test = False
        self.batch = False
        self.config = RaffleConfiguration.query.first()
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
        self.balance = self.get_list_balance(self.selected_dancers + self.confirmed_dancers)
        self.registered_groups = self.groups(REGISTERED)
        self.selected_groups = self.groups(SELECTED)
        self.confirmed_groups = self.groups(CONFIRMED)
        self.no_partner_groups = []
        self.group_lists = {REGISTERED: self.registered_groups, SELECTED: self.selected_groups,
                            CONFIRMED: self.confirmed_groups, self.NO_PARTNER: self.no_partner_groups}

    def groups(self, source):
        source = self.dancer_lists[source]
        groups = [DancingGroup(d) for d in source
                  if d.get_dancing_info(BALLROOM).partner is None and d.get_dancing_info(LATIN).partner is None]
        dancers_with_partners = [dancer for dancer in source
                                 if dancer.get_dancing_info(BALLROOM).partner is not None
                                 or dancer.get_dancing_info(LATIN).partner is not None]
        while len(dancers_with_partners) > 0:
            group = DancingGroup()
            group.add_chain(group.check_chain(dancers_with_partners[0], source), source)
            groups.append(group)
            for dancer in group.dancers:
                try:
                    dancers_with_partners.remove(dancer)
                except ValueError:
                    pass
        return groups

    def update_balance(self):
        self.balance = self.get_list_balance(self.selected_dancers + self.confirmed_dancers)

    def team_captains(self):
        return [dancer for dancer in self.registered_dancers if dancer.contestant_info.team_captain]

    def number_of_team_captains(self):
        return len(self.team_captains())

    def sleeping_spots(self):
        return [d for d in self.selected_dancers + self.confirmed_dancers if d.additional_info.sleeping_arrangements]

    def number_of_sleeping_spots(self):
        return len(self.sleeping_spots()) + \
               len(SuperVolunteer.query.filter(SuperVolunteer.sleeping_arrangements.is_(True)).all())

    def first_time_dancers(self):
        return [dancer for dancer in self.registered_dancers if dancer.contestant_info.first_time]

    def not_selected_last_time_dancers(self):
        nsd = NotSelectedContestant.query.filter(NotSelectedContestant.tournament == g.sc.tournament).all()
        nsd_names = [d.get_full_name() for d in nsd]
        nsd_emails = [d.email.lower() for d in nsd]
        return [dancer for dancer in self.registered_dancers if dancer.get_full_name()
                in nsd_names or dancer.email.lower() in nsd_emails]

    def number_of_first_time_dancers(self):
        return len(self.first_time_dancers())

    def newly_selected_dancers(self):
        return [d for d in self.selected_dancers if d.status_info.status == REGISTERED]

    def number_of_newly_selected_dancers(self):
        return len(self.newly_selected_dancers())

    def available_combinations(self, partners=False, source=REGISTERED):
        source_list = self.dancer_lists[source]
        if not partners:
            combination_dancers = [d for d in source_list if has_partners(d) is False]
        else:
            combination_dancers = [d for d in source_list]
        available_combinations_list = [get_combinations(d) for d in combination_dancers]
        sorted_list = sort_combinations(available_combinations_list)
        available_combinations = {comb: 0 for comb in sorted_list}
        for comb in available_combinations_list:
            available_combinations[comb] += 1
        return available_combinations

    def get_dancer_list(self, dancer):
        for k, l in self.dancer_lists.items():
            if dancer in l:
                return k

    def move_dancer_to_list(self, dancer, list_to):
        list_from = self.get_dancer_list(dancer)
        while dancer in self.dancer_lists[list_from]:
            self.dancer_lists[list_from].remove(dancer)
        self.dancer_lists[list_to].append(dancer)

    def select_dancer(self, dancer):
        self.move_dancer_to_list(dancer, SELECTED)

    def reset_dancer(self, dancer):
        self.move_dancer_to_list(dancer, REGISTERED)

    def no_partner_found(self, dancer):
        self.move_dancer_to_list(dancer, self.NO_PARTNER)

    def reset_no_partner_dancers(self):
        while len(self.no_partner_list) > 0:
            dancer = self.no_partner_list[0]
            self.reset_dancer(dancer)

    def get_group_list(self, group):
        for k, l in self.group_lists.items():
            if group in l:
                return k

    def move_group_to_list(self, group, list_to):
        list_from = self.get_group_list(group)
        self.group_lists[list_from].remove(group)
        self.group_lists[list_to].append(group)

    def move_selected_group(self, groups):
        for grp in groups:
            self.move_group_to_list(grp, SELECTED)
            for dancer in grp.dancers:
                self.select_dancer(dancer)

    def no_partner_found_group(self, groups):
        for grp in groups:
            self.move_group_to_list(grp, self.NO_PARTNER)
            for dancer in grp.dancers:
                self.no_partner_found(dancer)

    def reset_group(self, group):
        self.move_group_to_list(group, REGISTERED)

    def reset_no_partner_groups(self):
        while len(self.no_partner_groups) > 0:
            print(f'Placing {self.no_partner_groups[0].dancers} back onto registered list.')
            self.reset_group(self.no_partner_groups[0])
        self.reset_no_partner_dancers()

    def select_groups(self, groups):
        self.move_selected_group(groups)
        self.update_balance()

    def number_of_selected_dancers(self):
        return len(self.selected_dancers) + len(self.confirmed_dancers)

    def full(self):
        return self.number_of_selected_dancers() >= self.config.maximum_number_of_dancers

    def almost_full(self):
        return (len(self.selected_dancers) + len(self.confirmed_dancers)) > (self.config.maximum_number_of_dancers - 2)

    def raffle_complete(self):
        return len(self.selected_dancers) >= (self.config.maximum_number_of_dancers - self.config.selection_buffer)

    def exceed_max(self, groups):
        groups_dancers = []
        for grp in groups:
            groups_dancers += grp.dancers
        return (len(self.selected_dancers) + len(self.confirmed_dancers) +
                len(groups_dancers)) > self.config.maximum_number_of_dancers

    def beginners(self):
        return [dancer for dancer in self.registered_dancers
                if dancer.dancing_information(BALLROOM).level == BEGINNERS
                or dancer.dancing_information(LATIN).level == BEGINNERS]

    def number_of_beginners(self):
        return len(self.beginners())

    def selected_beginners(self):
        return [dancer for dancer in self.selected_dancers
                if dancer.dancing_information(BALLROOM).level == BEGINNERS
                or dancer.dancing_information(LATIN).level == BEGINNERS]

    def lions(self):
        return [dancer for dancer in self.registered_dancers
                if dancer.dancing_information(BALLROOM).level in [BEGINNERS, BREITENSPORT]
                or dancer.dancing_information(LATIN).level in [BEGINNERS, BREITENSPORT]]

    # def number_of_lions(self):
    #     return len(self.lions())

    def selected_lions(self):
        return [dancer for dancer in self.selected_dancers
                if dancer.dancing_information(BALLROOM).level in [BEGINNERS, BREITENSPORT]
                or dancer.dancing_information(LATIN).level in [BEGINNERS, BREITENSPORT]]

    def selected_per_team(self, source):
        if source == BEGINNERS:
            return self.selected_beginners()
        if source == LIONS:
            return self.selected_lions()

    def guaranteed_dancers(self):
        guaranteed_dancers = [dancer for dancer in (self.registered_dancers + self.no_partner_list)
                              if dancer.status_info.guaranteed_entry or dancer.contestant_info.team_captain]
        if self.config.first_time_guaranteed_entry:
            guaranteed_dancers += self.first_time_dancers()
        return guaranteed_dancers

    def number_of_guaranteed_dancers(self):
        return len(self.guaranteed_dancers())

    def update_states(self):
        if not self.test and not self.batch:
            for dancer in self.registered_dancers:
                dancer.status_info.raffle_status = REGISTERED
            for dancer in self.selected_dancers:
                dancer.status_info.raffle_status = SELECTED
            for dancer in self.confirmed_dancers:
                dancer.status_info.raffle_status = CONFIRMED
            db.session.commit()

    @staticmethod
    def get_empty_stats():
        return {lvl: {cat: {LEAD: 0, FOLLOW: 0, DIFF: 0} for cat in ALL_COMPETITIONS}
                for lvl in g.sc.get_participating_levels()}

    def update_stats(self, source_list):
        stats = self.get_empty_stats()
        for d in source_list:
            for info in d.dancing_info:
                if info.level != NO:
                    stats[info.level][info.competition][info.role] += 1
        for _, cat in stats.items():
            for _, comp in cat.items():
                comp[DIFF] = comp[LEAD] - comp[FOLLOW]
        return stats

    def get_stats(self, status):
        stats = self.get_empty_stats()
        if status == CONFIRMED:
            stats = self.update_stats(self.confirmed_dancers)
        if status == SELECTED:
            stats = self.update_stats(self.selected_dancers)
        if status == REGISTERED:
            stats = self.update_stats(self.registered_dancers)
        if status == REGISTERED + SELECTED:
            stats = self.update_stats(self.registered_dancers + self.selected_dancers)
        if status == SELECTED + CONFIRMED:
            stats = self.update_stats(self.selected_dancers + self.confirmed_dancers)
        return stats

    def cutoff(self):
        if self.config.selection_buffer == 0:
            cutoff = self.config.maximum_number_of_dancers - 4 * self.number_of_guaranteed_dancers()
        else:
            cutoff = self.config.maximum_number_of_dancers - self.config.selection_buffer - \
                     3 * self.number_of_guaranteed_dancers()
        return cutoff

    def is_balanced(self, exclude=None):
        balance = Balance(self.selected_dancers + self.confirmed_dancers)
        if exclude is not None:
            balance.set_zero(exclude)
        return balance.balanced()

    def is_group_reducing_balance(self, group):
        system_balance_sum = self.balance_sum()
        balance_after = Balance(self.selected_dancers + self.confirmed_dancers)
        balance_after.add_balance(group.balance)
        balance_after_sum = balance_after.balance_sum()
        if system_balance_sum == 0:
            return False
        return balance_after_sum < system_balance_sum

    def specific_groups(self, dancers_source, team=None):
        if dancers_source == BEGINNERS:
            dancers = self.beginners()
        elif dancers_source == LIONS:
            dancers = self.lions()
        elif dancers_source == FIRST_TIME:
            dancers = self.first_time_dancers()
        elif dancers_source == NOT_SELECTED_LAST_TIME:
            dancers = self.not_selected_last_time_dancers()
        else:
            return []
        if team is not None:
            dancers = [d for d in dancers if d.contestant_info.team == team]
        groups = []
        for grp in self.registered_groups:
            for d in grp.dancers:
                if d in dancers:
                    groups += [grp]
                    break
        return groups

    def guaranteed_groups(self, balanced=None):
        guaranteed_groups = []
        guaranteed_dancers = self.guaranteed_dancers()
        for grp in self.registered_groups:
            if True in [d in guaranteed_dancers for d in grp.dancers]:
                guaranteed_groups.append(grp)
        if balanced is not None:
            if balanced:
                return [grp for grp in guaranteed_groups if grp.balanced()]
            else:
                return [grp for grp in guaranteed_groups if not grp.balanced()]
        return guaranteed_groups

    @staticmethod
    def lion_contestants(list_of_dancers):
        team_lions = 0
        for dancer in list_of_dancers:
            for di in dancer.dancing_info:
                if di.level in [BEGINNERS, BREITENSPORT]:
                    team_lions += 1
        return team_lions

    def start_message(self):
        if not self.test and not self.batch:
            print('Starting automated raffle.')
            # Rearrange numbers of all dancers
            rearrange_numbers()
        elif self.test:
            print('Starting test raffle.')
        elif self.batch:
            print('Starting batch of raffles.')

    def raffle(self):
        start_time = time.time()

        # Start raffle
        self.start_message()

        # Guaranteed dancers
        self.select_guaranteed_balanced_groups()
        self.select_guaranteed_unbalanced_groups()

        # Select all Beginners if option selected
        if self.config.beginners_guaranteed_entry_cutoff and self.number_of_beginners() <= \
                self.config.beginners_guaranteed_cutoff:
            self.select_all_beginners_groups()
            self.balance_raffle(exclude=BEGINNERS, update=False)
        # Guaranteed number of Beginners per team
        if self.config.beginners_guaranteed_per_team:
            self.select_guaranteed_dancers_per_team(BEGINNERS)
        # Guaranteed number of Lions per team
        if self.config.lions_guaranteed_per_team:
            self.select_guaranteed_dancers_per_team(LIONS)

        # Main raffle
        self.raffle_groups()

        # Finish raffle
        self.close_raffle()

        print('Raffle done')
        print(f'{len(self.selected_dancers)} dancers selected')
        print("--- Raffle done in %.3f seconds ---" % (time.time() - start_time))

    def close_raffle(self):
        if not self.test and not self.batch:
            self.update_states()
        elif self.batch:
            dancer_ids = [0] + [d.contestant_id for d in Contestant.query.all()]
            selected = {did: 0 for did in dancer_ids}
            selected[0] = len(self.selected_dancers)
            for dancer in self.selected_dancers:
                selected[dancer.contestant_id] += 1

            with open('stats.txt', 'a', encoding='utf-8') as f1:
                f1.write(str(selected) + '\n')

            with open('stats_balance.txt', 'a', encoding='utf-8') as f1:
                f1.write(str(self.balance_sum()) + str(self.balance) + '\n')

    def orig_groups(self):
        increased_chance_groups = []
        if self.config.beginners_increased_chance:
            increased_chance_groups += self.specific_groups(BEGINNERS)
        if self.config.first_time_increased_chance:
            increased_chance_groups += self.specific_groups(FIRST_TIME)
        if self.config.not_selected_last_time_increased_chance:
            increased_chance_groups += self.specific_groups(NOT_SELECTED_LAST_TIME)
        return [grp for grp in self.registered_groups] + increased_chance_groups

    def select_guaranteed_balanced_groups(self):
        guaranteed_balanced = self.guaranteed_groups(balanced=True)
        guaranteed_unbalanced = self.guaranteed_groups(balanced=False)
        print('Guaranteed balanced groups')
        for grp in guaranteed_balanced:
            print(string_group_matched(grp))
        self.select_groups(guaranteed_balanced)
        print('Match guaranteed balanced groups amongst themselves')
        check_groups = [grp for grp in guaranteed_unbalanced]
        shuffle(guaranteed_unbalanced)
        for grp in guaranteed_unbalanced:
            if self.check_group_availability(grp):
                groups = self.find_partners_group(grp, source_groups=check_groups)
                for gr in groups:
                    try:
                        check_groups.remove(gr)
                    except ValueError:
                        pass
                if not self.exceed_max(groups):
                    self.add_groups(groups, remove_similar_groups=False)
            if len(check_groups) == 0:
                break
        self.reset_no_partner_groups()

    def select_guaranteed_unbalanced_groups(self):
        guaranteed_unbalanced = self.guaranteed_groups(balanced=False)
        for grp in guaranteed_unbalanced:
            if self.check_group_availability(grp):
                groups = self.find_partners_group(grp)
                if not self.exceed_max(groups):
                    self.add_groups(groups, guaranteed=True)

    def raffle_groups(self, guaranteed=False, save_extra_buffer=False):
        original_groups = self.orig_groups()
        r = list(range(0, len(original_groups)))
        shuffle(r)
        for i in r:
            if not self.raffle_complete() and not self.almost_full():
                try:
                    group = original_groups[i]
                except IndexError:
                    pass
                else:
                    if self.check_group_availability(group):
                        if group.check():
                            groups = [group]
                        else:
                            groups = self.find_partners_group(group)
                        if not self.exceed_max(groups):
                            self.add_groups(groups, guaranteed=guaranteed)
                    if save_extra_buffer:
                        counter = self.number_of_selected_dancers()
                        cutoff = self.cutoff()
                        print(f"Count: {counter}")
                        print(f"Cutoff: {cutoff}")
                        if counter >= cutoff:
                            break
            else:
                break
        self.reset_no_partner_groups()

    def find_partners_group(self, group, source_groups=None):
        print('LFG: {}'.format(group.dancers))
        possible_groups = []
        if source_groups is not None:
            groups = [grp for grp in source_groups if not grp.balanced()]
        else:
            groups = [grp for grp in self.registered_groups if not grp.balanced()]
        if group.completable():
            target_balance = group.get_opposite_balance()
            for grp in groups:
                if grp.balance == target_balance:
                    possible_groups.append([group, grp])
        for i in range(0, len(groups)):
            temp_grp = DancingGroup()
            temp_grp.add_group(group)
            temp_grp.add_group(groups[i])
            if temp_grp.completable():
                target_balance = temp_grp.get_opposite_balance()
                for j in range(i + 1, len(groups)):
                    if groups[j].balance == target_balance:
                        possible_groups.append([group, groups[i], groups[j]])
        if len(possible_groups) == 0:
            if delft_exception(group):
                group.delft_exception = True
                if group.completable():
                    for grp in groups:
                        temp_grp = DancingGroup()
                        temp_grp.add_group(group)
                        temp_grp.add_group(grp)
                        if temp_grp.balance_sum() < group.balance_sum():
                            possible_groups.append([group, grp])
        if len(possible_groups) == 0:
            for i in range(0, len(groups)):
                for j in range(i + 1, len(groups)):
                    temp_grp = DancingGroup()
                    temp_grp.add_group(group)
                    temp_grp.add_group(groups[i])
                    temp_grp.add_group(groups[j])
                    if temp_grp.completable():
                        target_balance = temp_grp.get_opposite_balance()
                        for k in range(i + 2, len(groups)):
                            if groups[k].balance == target_balance:
                                possible_groups.append([group, groups[i], groups[j], groups[k]])
        if len(possible_groups) == 0:
            possible_groups.append([group])
        shuffle(possible_groups)
        return possible_groups[0]

    def select_all_beginners_groups(self):
        beginners_groups = self.specific_groups(BEGINNERS)
        check_groups = [grp for grp in self.registered_groups if grp in beginners_groups]
        shuffle(beginners_groups)
        for grp in beginners_groups:
            if self.check_group_availability(grp):
                if grp.check():
                    groups = [grp]
                else:
                    groups = self.find_partners_group(grp, source_groups=check_groups)
                if not self.exceed_max(groups):
                    self.add_groups(groups, guaranteed=True, remove_similar_groups=False)
                for gr in groups:
                    try:
                        check_groups.remove(gr)
                    except ValueError:
                        pass
            if len(check_groups) == 0:
                break
        self.reset_no_partner_groups()

    def select_guaranteed_dancers_per_team(self, dancers_source=None):
        if dancers_source is not None:
            if dancers_source == BEGINNERS:
                guaranteed_dancers = self.beginners()
                maximum_dancers = self.config.beginners_minimum_entry_per_team
                selected_dancers_source = self.selected_beginners()
            else:
                guaranteed_dancers = self.lions()
                maximum_dancers = int(2*self.config.lions_minimum_entry_per_team)
                selected_dancers_source = self.selected_lions()
            log_file = f"stats_{dancers_source.lower()}"
            all_team_captains = User.query.filter(User.access == ACCESS[TEAM_CAPTAIN], User.is_active.is_(True)).all()
            all_teams = [team_captain.team for team_captain in all_team_captains]
            ordered_teams = []
            for team in all_teams:
                team_dancers = [d for d in guaranteed_dancers if d.contestant_info.team == team]
                selected_team_dancers = [d for d in selected_dancers_source if d.contestant_info.team == team]
                if dancers_source == BEGINNERS:
                    count = len(team_dancers) + len(selected_team_dancers)
                else:
                    count = []
                    for d in team_dancers + selected_team_dancers:
                        for di in d.dancing_info:
                            if di.level in [BREITENSPORT, BEGINNERS]:
                                count.append(1)
                    count = len(count)
                ordered_teams += [{'team': team, 'max_dancers': min(count, maximum_dancers)}]
            for _ in range(0, len(guaranteed_dancers)):
                for team in ordered_teams:
                    selected_dancers = [d for d in self.selected_dancers if
                                        d.contestant_info.team == team['team']]
                    team['dancers'] = self.specific_groups(dancers_source, team=team['team'])
                    if dancers_source == BEGINNERS:
                        team['number_of_dancers'] = len([d for d in selected_dancers if d in
                                                         self.selected_per_team(dancers_source)])
                    else:
                        team['number_of_dancers'] = self.lion_contestants(selected_dancers)
                shuffle(ordered_teams)
                ordered_teams.sort(key=lambda x: (x['number_of_dancers']+1)/(x['max_dancers']+1))
                for team_list in ordered_teams:
                    if (team_list['max_dancers'] - team_list['number_of_dancers']) > 0 and len(
                            team_list['dancers']) > 0:
                        shuffle(team_list['dancers'])
                        for grp in team_list['dancers']:
                            if not self.raffle_complete() and not self.almost_full():
                                if self.check_group_availability(grp):
                                    if grp.check():
                                        groups = [grp]
                                    else:
                                        groups = []
                                        for team in ordered_teams:
                                            groups = self.find_partners_group(grp, source_groups=team['dancers'])
                                            if groups != [grp]:
                                                break
                                    if not self.exceed_max(groups):
                                        self.add_groups(groups)
                                        break
                        break
                else:
                    break
            self.reset_no_partner_groups()
            if self.batch:
                ordered_teams.sort(key=lambda x: x['team'].team_id)
                str_list = []
                for team in ordered_teams:
                    str_list += [team['team'].name]
                for team in ordered_teams:
                    str_list += [str(team['number_of_dancers'])]
                for team in ordered_teams:
                    str_list += [str(team['max_dancers'])]
                str_list = ','.join(str_list)
                with open(f'{log_file}.txt', 'a', encoding='utf-8') as f1:
                    f1.write(str_list + '\n')

    def balance_raffle(self, exclude=None, update=True):
        original_groups = [grp for grp in self.registered_groups if grp.balance_sum() > 0]
        r = list(range(0, len(original_groups)))
        shuffle(r)
        for i in r:
            if not self.almost_full() and not self.is_balanced(exclude=exclude):
                try:
                    group = original_groups[i]
                except IndexError:
                    pass
                else:
                    if not self.exceed_max([group]) and self.is_group_reducing_balance(group):
                        self.add_groups([group], guaranteed=True, reducing_difference=True)
            else:
                break
        self.reset_no_partner_groups()
        if update:
            self.update_states()
        flash('Balancing attempt done.')

    def finish_raffle(self, non_sleeping_hall_dancers=False):
        if not non_sleeping_hall_dancers:
            self.balance_raffle()
        original_groups = self.orig_groups()
        r = list(range(0, len(self.registered_groups)))
        shuffle(r)
        if not self.almost_full():
            for i in r:
                try:
                    group = original_groups[i]
                except IndexError:
                    pass
                else:
                    if self.check_group_availability(group):
                        if group.check():
                            groups = [group]
                        else:
                            groups = self.find_partners_group(group)
                        if not self.exceed_max(groups):
                            admissible = True
                            if non_sleeping_hall_dancers:
                                groups_dancers = []
                                for grp in groups:
                                    groups_dancers += grp.dancers
                                admissible = len([d for d in groups_dancers
                                                  if not d.additional_info
                                                 .sleeping_arrangements]) == len(groups_dancers)
                            if admissible:
                                self.add_groups(groups)
                                if self.almost_full():
                                    break
        self.update_states()
        flash('Adding of groups done.')

    def add_neutral_group(self):
        message = 'Could not find a neutral group.'
        if not self.full():
            original_groups = [grp for grp in self.registered_groups]
            r = list(range(0, len(self.registered_groups)))
            shuffle(r)
            for i in r:
                try:
                    group = original_groups[i]
                except IndexError:
                    pass
                else:
                    if self.check_group_availability(group):
                        if group.check():
                            groups = [group]
                        else:
                            groups = self.find_partners_group(group)
                        if not self.exceed_max(groups) and self.check_list_of_groups(groups):
                            self.add_groups(groups)
                            self.update_states()
                            print_group = DancingGroup(dancers_input=[d for grp in groups for d in grp.dancers])
                            message = 'Selected {}.'.format(print_group.get_dancers_summary())
                            break
        else:
            message = f"The maximum number of dancers ({self.config.maximum_number_of_dancers}) has been reached. " \
                      f"You cannot add more dancers."
        return message

    def select_single_dancer(self, form):
        message = 'Could not find a neutral group.'
        if not self.full():
            try:
                combination = [f for f in form][0]
            except IndexError:
                combination = None
            if combination is not None:
                dancers = [d for d in self.registered_dancers if check_combination(d, combination)]
                original_groups = self.find_dancers_groups(dancers, REGISTERED)
                r = list(range(0, len(original_groups)))
                shuffle(r)
                for i in r:
                    try:
                        group = original_groups[i]
                    except IndexError:
                        pass
                    else:
                        if self.check_group_availability(group):
                            if group.check():
                                groups = [group]
                            else:
                                groups = self.find_partners_group(group)
                            if not self.exceed_max(groups) and self.check_list_of_groups(groups):
                                self.add_groups(groups)
                                self.update_states()
                                print_group = DancingGroup(dancers_input=[d for grp in groups for d in grp.dancers])
                                message = 'Selected {}.'.format(print_group.get_dancers_summary())
                                break
        else:
            message = f"The maximum number of dancers ({self.config.maximum_number_of_dancers}) has been reached. " \
                      f"You cannot add more dancers."
        return message

    def select_specific_dancers(self, form):
        if not self.full():
            dancers = [d for d in self.registered_dancers if f"specific-{d.contestant_id}" in form]
            groups = self.find_dancers_groups(dancers, REGISTERED)
            if not self.exceed_max(groups):
                self.add_groups(groups, guaranteed=True)
                self.update_states()
                print_group = DancingGroup(dancers_input=[d for grp in groups for d in grp.dancers])
                message = 'Selected {}.'.format(print_group.get_dancers_summary())
            else:
                message = "Cannot add dancers selected dancers. Doing so would exceed the limit."
        else:
            message = f"The maximum number of dancers ({self.config.maximum_number_of_dancers}) has been reached. " \
                      f"You cannot add more dancers."
        return message

    def confirm_selection(self, dancers):
        groups = self.find_dancers_groups(dancers, SELECTED)
        for grp in groups:
            self.add_groups(groups)
            for dancer in grp.dancers:
                dancer.status_info.set_status(SELECTED)
                teamcaptain = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                                User.team == dancer.contestant_info.team).first()
                text = f"{dancer.get_full_name()} has been selected for the tournament by the raffle system.\n"
                n = Notification(title=f"Selected {dancer.get_full_name()} for the tournament", text=text,
                                 user=teamcaptain)
                n.send()
        flash('Marked dancers are now selected and this is visible to the teamcaptains.')
        db.session.commit()

    def cancel_selection(self, dancers):
        groups = self.find_dancers_groups(dancers, SELECTED)
        for grp in groups:
            self.reset_group(grp)
            for dancer in grp.dancers:
                dancer.status_info.set_status(REGISTERED)
        flash('Marked dancers are put back into the raffle selection pool.')
        db.session.commit()

    def find_dancers_groups(self, dancers, status):
        groups = []
        for d in dancers:
            grp = self.find_dancer_group(d, status)
            if grp not in groups:
                groups.append(grp)
        return groups

    def find_dancer_group(self, dancer, status):
        for grp in self.group_lists[status]:
            if dancer in grp.dancers:
                return grp

    def check_group_availability(self, group):
        for dancer in group.dancers:
            if dancer not in self.registered_dancers:
                return False
        return True

    def check_list_of_groups(self, groups, guaranteed=False):
        add = False
        group = DancingGroup()
        for grp in groups:
            group.add_group(grp)
            if grp.delft_exception:
                group.delft_exception = True
        if group.delft_exception and not guaranteed:
            if self.balance_sum() < 8:
                guaranteed = True
        if group.check():
            add = True
        elif not group.check() and guaranteed:
            add = True
        return add

    def add_groups(self, groups, guaranteed=False, reducing_difference=False, remove_similar_groups=True):
        add = self.check_list_of_groups(groups, guaranteed=guaranteed)
        group = DancingGroup()
        for grp in groups:
            group.add_group(grp)
            if grp.delft_exception:
                group.delft_exception = True
        if group.check():
            print(string_group_matched(group))
        elif not group.check() and add:
            if reducing_difference:
                print(string_group_matched_incomplete_reducing_difference(group))
            elif len([d for d in group.dancers if d.contestant_info.team_captain]) > 0:
                print(string_group_matched_incomplete_team_captain_exception(group))
            else:
                print(string_group_guaranteed_exception(group))
        else:
            print(string_group_no_partner(group))
        if add:
            self.select_groups(groups)
        else:
            self.no_partner_found_group(groups)
            if remove_similar_groups:
                if not guaranteed:
                    similar_groups = [grp for grp in self.registered_groups if grp.balance == group.balance]
                    self.no_partner_found_group(similar_groups)
