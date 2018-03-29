from raffle_system.functions import *
import random


def select_groups(dl, list_of_dancers, guaranteed=False):
    r = range(0, len(list_of_dancers))
    for _ in r:
        if not dl.complete():
            try:
                dancer = random.choice(list_of_dancers)
            except IndexError:
                pass
            else:
                if dl.check_availability(dancer):
                    group = find_partners(dl.list(REGISTERED), dancer)
                    dl.add_group(group, guaranteed=guaranteed)
        else:
            break


def raffle(guaranteed_dancers=None):
    # rearrange_numbers()
    dancer_lists = DancerLists()

    # Select teamcaptains
    select_groups(dancer_lists, dancer_lists.teamcaptains(), guaranteed=True)

    # Select guaranteed dancers
    if guaranteed_dancers is not None:
        select_groups(dancer_lists, guaranteed_dancers, guaranteed=True)

    # Select other dancers
    select_groups(dancer_lists, dancer_lists.list(REGISTERED))

    # Update raffle states
    dancer_lists.update_states()
    print('Raffle done')
    print(f'{len(dancer_lists.selected_dancers)} dancers selected')

    # for dancer in dancer_lists.selected_dancers:
    #     if random.choice([True, False]):
    #         dancer_lists.move_dancer_to_list(dancer, CONFIRMED)
    #         dancer.status_info[0].set_status(CONFIRMED)
    #     else:
    #         dancer.status_info[0].set_status(SELECTED)
    # dancer_lists.update_states()


def test_raffle(selected):
    print('Starting test raffle.')
    dancer_lists = DancerLists()

    # Select teamcaptains
    select_groups(dancer_lists, dancer_lists.teamcaptains(), guaranteed=True)

    # Select other dancers
    select_groups(dancer_lists, dancer_lists.list(REGISTERED))

    print('Done with test raffle')

    selected_dancers = dancer_lists.list(SELECTED)
    selected[0] = len(selected_dancers)
    for dancer in selected_dancers:
        selected[dancer.contestant_id] += 1

    return selected


