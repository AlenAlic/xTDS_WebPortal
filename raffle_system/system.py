from raffle_system.functions import *
import random


def select_groups(raffle_sys, list_of_dancers, guaranteed=False):
    r = list(range(0, len(list_of_dancers)))
    shuffle(r)
    for i in r:
        if not raffle_sys.complete():
            try:
                if not guaranteed:
                    dancer = random.choice(list_of_dancers)
                else:
                    dancer = list_of_dancers[i]
            except IndexError:
                pass
            else:
                if raffle_sys.check_availability(dancer):
                    group = find_partners(raffle_sys.registered_dancers, dancer)
                    # print('Group balance sum:')
                    # print(raffle_sys.get_balance_sum(group.get_balance()))
                    raffle_sys.add_group(group, guaranteed=guaranteed)
                    # print('Total balance sum:')
                    # print(raffle_sys.get_balance_sum(raffle_sys.get_balance()))
        else:
            break


def raffle(raffle_sys, guaranteed_dancers=None):
    # rearrange_numbers()
    # dancer_lists = DancerLists()

    # Select teamcaptains
    select_groups(raffle_sys, raffle_sys.teamcaptains(), guaranteed=True)

    # Select guaranteed dancers
    if guaranteed_dancers is not None:
        select_groups(raffle_sys, guaranteed_dancers, guaranteed=True)

    # Select other dancers
    select_groups(raffle_sys, raffle_sys.registered_dancers)

    # Update raffle states
    raffle_sys.update_states()
    print('Raffle done')
    print(f'{len(raffle_sys.selected_dancers)} dancers selected')

    # for dancer in dancer_lists.selected_dancers:
    #     if random.choice([True, False]):
    #         dancer_lists.move_dancer_to_list(dancer, CONFIRMED)
    #         dancer.status_info[0].set_status(CONFIRMED)
    #     else:
    #         dancer.status_info[0].set_status(SELECTED)
    # dancer_lists.update_states()

    return raffle_sys


def test_raffle(selected):
    print('Starting test raffle.')
    raffle_sys = RaffleSystem()

    # Select teamcaptains
    select_groups(raffle_sys, raffle_sys.teamcaptains(), guaranteed=True)

    # Select other dancers
    select_groups(raffle_sys, raffle_sys.registered_dancers)

    print('Done with test raffle')

    selected_dancers = raffle_sys.selected_dancers
    selected[0] = len(selected_dancers)
    for dancer in selected_dancers:
        selected[dancer.contestant_id] += 1

    return selected


