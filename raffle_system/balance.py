from flask import g
from ntds_webportal.data import *


class Balance:
    measure = {LEAD: 1, FOLLOW: -1, NO: 0}

    def __init__(self, dancers_input=None):
        if dancers_input is None:
            self.balance = self.get_empty_balance()
        else:
            if isinstance(dancers_input, list):
                self.balance = self.get_list_balance(dancers_input)
            else:
                self.balance = self.get_dancer_balance(dancers_input)

    def get_balance(self):
        return self.balance

    @staticmethod
    def get_empty_balance():
        return {comp: {lvl: 0 for lvl in g.sc.get_participating_levels() + [NO]} for comp in ALL_COMPETITIONS}

    def set_balance(self, balance):
        self.balance = balance
        return self.balance

    def set_empty_balance(self):
        self.balance = self.get_empty_balance()

    def add_balance(self, new_balance):
        for comp, levels in new_balance.items():
            for lvl in levels:
                self.balance[comp][lvl] += new_balance[comp][lvl]

    def get_opposite_balance(self):
        opposite_balance = self.get_empty_balance()
        for comp, levels in self.balance.items():
            for lvl in levels:
                opposite_balance[comp][lvl] += self.balance[comp][lvl]
        for comp, levels in opposite_balance.items():
            for lvl in levels:
                opposite_balance[comp][lvl] *= -1
        return opposite_balance

    def join_balances(self, b1, b2):
        b = self.get_empty_balance()
        for comp, levels in b1.items():
            for lvl in levels:
                b[comp][lvl] += b1[comp][lvl]
                b[comp][lvl] += b2[comp][lvl]
        return b

    def balance_sum(self):
        counter = 0
        for _, lvl in self.balance.items():
            for level, bal in lvl.items():
                counter += abs(bal)
        return counter

    def balanced(self):
        return self.balance_sum() == 0

    def balance_values_completable(self):
        individual_values = [[abs(k) for k in v] for v in
                             [list(level.values()) for comp, level in self.balance.items()]]
        return all(sum(v) <= 1 for v in individual_values)

    def get_dancer_balance(self, dancer):
        balance = self.get_empty_balance()
        for di in dancer.dancing_info:
            balance[di.competition][di.level] += self.measure[di.role]
        return balance

    def get_list_balance(self, group_of_dancers):
        balance = self.get_empty_balance()
        for dancer in group_of_dancers:
            for di in dancer.dancing_info:
                balance[di.competition][di.level] += self.measure[di.role]
        return balance

    def completable(self):
        return self.balance_sum() <= 2 and self.balance_values_completable()

    def balance_values_completable_with_two_groups(self):
        individual_values = [[abs(k) for k in v] for v in
                             [list(level.values()) for comp, level in self.balance.items()]]
        return all(sum(v) <= 2 for v in individual_values)

    def completable_with_two_groups(self):
        return self.balance_sum() <= 4 and self.balance_values_completable_with_two_groups()

    def set_zero(self, exclude):
        if isinstance(exclude, str):
            exclude = [exclude]
        for comp in ALL_COMPETITIONS:
            for level in exclude:
                self.balance[comp][level] = 0
