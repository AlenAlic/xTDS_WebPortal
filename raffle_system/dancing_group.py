from ntds_webportal import db
from ntds_webportal.functions import get_dancing_categories, uniquify
from ntds_webportal.data import *
from raffle_system.balance import Balance
from raffle_system.functions import get_partners_ids


class DancingGroup(Balance):

    def __init__(self, dancers_input=None):
        super().__init__()
        self.dancers = []
        self.delft_exception = False
        if dancers_input is not None:
            if isinstance(dancers_input, list):
                self.add_dancers(dancers_input)
            else:
                self.add(dancers_input)

    def add(self, dancer):
        dancing_categories = get_dancing_categories(dancer.dancing_info)
        if dancer not in self.dancers:
            self.dancers.append(dancer)
            for _, di in dancing_categories.items():
                self.balance[di.competition][di.level] += self.measure[di.role]

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
        for _, groups in self.balance.items():
            balance.extend([m for _, m in groups.items()])
        return True if [number for number in balance if number == 0] == balance else False

    @staticmethod
    def check_chain(dancer, list_of_dancers):
        dancer_ids = [dancer.contestant_id]
        partner_ids = uniquify(get_partners_ids(dancer))
        if uniquify(get_partners_ids(dancer)) is not []:
            while dancer_ids != partner_ids:
                dancers = [d for d in list_of_dancers if d.contestant_id in dancer_ids]
                for d in dancers:
                    dancer_ids.extend(get_partners_ids(d))
                partners = [d for d in list_of_dancers if d.contestant_id in partner_ids]
                for d in partners:
                    partner_ids.extend(get_partners_ids(d))
                dancer_ids = uniquify(dancer_ids)
                partner_ids = uniquify(partner_ids)
                if len(partners) == 0:
                    break
            return dancer_ids
        else:
            return []

    def get_dancers_summary(self):
        f = '{name} ({team})'
        dancers = [f.format(name=d.get_full_name(), team=d.contestant_info[0].team.name) for d in self.dancers[:-1]]
        last_dancer = 'and {}'.format(f.format(name=self.dancers[-1].get_full_name(),
                                               team=self.dancers[-1].contestant_info[0].team.name))
        dancers.append(last_dancer)
        return ', '.join(dancers)

    def select_dancers(self):
        for dancer in self.dancers:
            dancer.status_info[0].raffle_status = SELECTED
        db.session.commit()
