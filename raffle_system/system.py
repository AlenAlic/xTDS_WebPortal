from raffle_system.functions import *
import time
import ast
from ntds_webportal.models import Contestant


def select_groups(raffle_sys, list_of_dancers, guaranteed=False):
    r = list(range(0, len(list_of_dancers)))
    shuffle(r)
    for i in r:
        if not raffle_sys.raffle_complete() and not raffle_sys.almost_full():
            try:
                if not guaranteed:
                    dancer = list_of_dancers[r[i]]
                else:
                    dancer = list_of_dancers[i]
            except IndexError:
                pass
            else:
                if raffle_sys.check_availability(dancer):
                    group = find_partners(raffle_sys.registered_dancers, dancer)
                    if not raffle_sys.exceed_max(group):
                        raffle_sys.add_group(group, guaranteed=guaranteed)
                        del group
        else:
            break


def raffle(raffle_sys, guaranteed_dancers=None):
    print('Starting automated raffle.')
    # Rearrange numbers of all dancers
    rearrange_numbers()
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
    return raffle_sys


def finish_raffle(raffle_sys):
    r = list(range(0, len(raffle_sys.registered_dancers)))
    shuffle(r)
    if not raffle_sys.almost_full():
        for i in r:
            try:
                dancer = raffle_sys.registered_dancers[r[i]]
            except IndexError:
                pass
            else:
                if raffle_sys.check_availability(dancer):
                    group = find_partners(raffle_sys.registered_dancers, dancer)
                    if not raffle_sys.exceed_max(group):
                        raffle_sys.add_group(group)
                        if raffle_sys.almost_full():
                            break
    raffle_sys.update_states()
    return raffle_sys


def raffle_add_neutral_group(raffle_sys):
    if not raffle_sys.full():
        r = list(range(0, len(raffle_sys.registered_dancers)))
        shuffle(r)
        for i in r:
            try:
                dancer = raffle_sys.registered_dancers[r[i]]
            except IndexError:
                pass
            else:
                if raffle_sys.check_availability(dancer):
                    group = find_partners(raffle_sys.registered_dancers, dancer)
                    if group.check():
                        raffle_sys.add_group(group)
                        group.select_dancers()
                        return 'Selected {}.'.format(group.get_dancers_summary())
        return 'Could not find a neutral group.'
    else:
        return f"The maximum number of dancers ({raffle_sys.raffle_config[MAX_DANCERS]}) has been reached. " \
               f"You cannot add more dancers."


def test_raffle(guaranteed_dancers=None):
    print('Starting test raffle.')
    start_time = time.time()
    raffle_sys = RaffleSystem()
    # Select teamcaptains
    select_groups(raffle_sys, raffle_sys.teamcaptains(), guaranteed=True)
    # Select guaranteed dancers
    if guaranteed_dancers is not None:
        select_groups(raffle_sys, guaranteed_dancers, guaranteed=True)
    # Select other dancers
    select_groups(raffle_sys, raffle_sys.registered_dancers)
    print('Done with test raffle')

    selected_dancers = raffle_sys.selected_dancers
    max_id = db.session.query().with_entities(db.func.max(Contestant.contestant_id)).scalar()
    dancer_ids = list(range(0, max_id + 1))
    selected = {did: 0 for did in dancer_ids}
    selected[0] = len(selected_dancers)
    for dancer in selected_dancers:
        selected[dancer.contestant_id] += 1

    with open('stats.txt', 'a', encoding='utf-8') as f1:
        f1.write(str(selected) + '\n')
    print("--- Test raffle done in %.3f seconds ---" % (time.time() - start_time))
    del raffle_sys


def export_stats_list():
    with open("stats.txt") as f:
        total = {}
        for line in f:
            d = ast.literal_eval(line)
            if len(total) > 0:
                for k, v in d.items():
                    total[k] += v
            else:
                total = d
    with open('stats_list.txt', 'w', encoding='utf-8') as f1:
        for _, v in total.items():
            f1.write(str(v) + '\n')
