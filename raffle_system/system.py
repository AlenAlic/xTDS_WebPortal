from raffle_system.functions import *


def raffle():
    # Select teamcaptains
    dancer_lists = DancerLists()
    team_captains = dancer_lists.teamcaptains()
    for tc in team_captains:
        if dancer_lists.check_availability(tc):
            group = find_partners(dancer_lists.list(REGISTERED), tc)
            dancer_lists.add_group(group, teamcaptain=True)
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


def test_raffle(selected):
    # rearrange_numbers()
    dancer_lists = DancerLists()
    team_captains = dancer_lists.teamcaptains()
    for tc in team_captains:
        if dancer_lists.check_availability(tc):
            group = find_partners(dancer_lists.list(REGISTERED), tc)
            dancer_lists.add_group(group, teamcaptain=True)

    test_dancer = db.session.query(Contestant).filter(Contestant.contestant_id == 83).first()
    group = find_partners(dancer_lists.list(REGISTERED), test_dancer)
    dancer_lists.add_group(group)

    remaining_dancers = dancer_lists.list(REGISTERED)
    shuffle(remaining_dancers)
    for dancer in remaining_dancers:
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


