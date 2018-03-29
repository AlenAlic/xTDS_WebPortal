from raffle_system.functions import *
import random


def raffle(guaranteed_dancers=None):
    rearrange_numbers()
    # Select teamcaptains
    dancer_lists = DancerLists()
    team_captains = dancer_lists.teamcaptains()
    for tc in team_captains:
        if not dancer_lists.complete():
            if dancer_lists.check_availability(tc):
                group = find_partners(dancer_lists.list(REGISTERED), tc)
                dancer_lists.add_group(group, guaranteed=True)
        else:
            break
    # Select guaranteed dancers
    if guaranteed_dancers is not None:
        for dancer in guaranteed_dancers:
            if not dancer_lists.complete():
                if dancer_lists.check_availability(dancer):
                    group = find_partners(dancer_lists.list(REGISTERED), dancer)
                    dancer_lists.add_group(group, guaranteed=True)
            else:
                break
    # Select other dancers
    remaining_dancers = dancer_lists.list(REGISTERED)
    shuffle(remaining_dancers)
    for dancer in remaining_dancers:
        if not dancer_lists.complete():
            if dancer_lists.check_availability(dancer):
                group = find_partners(dancer_lists.list(REGISTERED), dancer)
                dancer_lists.add_group(group)
        else:
            break
    # Update raffle states
    dancer_lists.update_states()

    print('Raffle done')


def test_raffle(selected):
    print('Starting test raffle.')
    rearrange_numbers()
    dancer_lists = DancerLists()
    team_captains = dancer_lists.teamcaptains()
    for tc in team_captains:
        if dancer_lists.check_availability(tc):
            group = find_partners(dancer_lists.list(REGISTERED), tc)
            dancer_lists.add_group(group, guaranteed=True)

    random_order_list = list(range(0, len(dancer_lists.list(REGISTERED))))
    shuffle(random_order_list)
    for i in random_order_list:
        dancer = dancer_lists.list(REGISTERED)[i] if i < len(dancer_lists.list(REGISTERED)) else None
        if dancer is not None:
            if not dancer_lists.complete():
                if dancer_lists.check_availability(dancer):
                    group = find_partners(dancer_lists.list(REGISTERED), dancer)
                    dancer_lists.add_group(group)
            else:
                break

    # dancer_lists.update_states()
    selected_dancers = dancer_lists.list(SELECTED)
    selected[0] = len(selected_dancers)
    for dancer in selected_dancers:
        selected[dancer.contestant_id] += 1
    print('Done')
    return selected


