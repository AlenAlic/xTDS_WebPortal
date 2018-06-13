from ntds_webportal.tournament_config import *
from raffle_system.raffle_config import *

# Access levels
ACCESS = {
    'admin': 0,
    'organizer': 1,
    'blind_date_organizer': 2,
    'team_captain': 3,
    'treasurer': 4
}

# All possible teams
TEAMS = [
    {'country': NETHERLANDS, 'name': '4 happy feet', 'city': 'Enschede'},
    {'country': NETHERLANDS, 'name': 'AmsterDance', 'city': 'Amsterdam'},
    {'country': NETHERLANDS, 'name': 'Blue Suede Shoes', 'city': 'Delft'},
    {'country': NETHERLANDS, 'name': 'Dance Fever', 'city': 'Nijmegen'},
    {'country': NETHERLANDS, 'name': 'Erasmus Dance Society', 'city': 'Rotterdam'},
    {'country': NETHERLANDS, 'name': 'Footloose', 'city': 'Eindhoven'},
    {'country': NETHERLANDS, 'name': 'LeiDance', 'city': 'Leiden'},
    {'country': NETHERLANDS, 'name': 'Let`s Dance', 'city': 'Maastricht'},
    {'country': NETHERLANDS, 'name': 'The Blue Toes', 'city': 'Groningen'},
    {'country': NETHERLANDS, 'name': 'U Dance', 'city': 'Utrecht'},
    {'country': NETHERLANDS, 'name': 'WUBDA', 'city': 'Wageningen'},
    {'country': GERMANY, 'name': 'Unitanz Aachen', 'city': 'Aachen'},
    {'country': GERMANY, 'name': 'Unitanz Antibes', 'city': 'Antibes'},
    {'country': GERMANY, 'name': 'Unitanz Berlin', 'city': 'Berlin'},
    {'country': GERMANY, 'name': 'Unitanz Bielefeld', 'city': 'Bielefeld'},
    {'country': GERMANY, 'name': 'Unitanz Bonn', 'city': 'Bonn'},
    {'country': GERMANY, 'name': 'Unitanz Clausthal', 'city': 'Clausthal'},
    {'country': GERMANY, 'name': 'Unitanz Cottbus', 'city': 'Cottbus'},
    {'country': GERMANY, 'name': 'Unitanz Darmstadt', 'city': 'Darmstadt'},
    {'country': GERMANY, 'name': 'Unitanz Dortmund', 'city': 'Dortmund'},
    {'country': GERMANY, 'name': 'Unitanz Düsseldorf', 'city': 'Düsseldorf'},
    {'country': GERMANY, 'name': 'Unitanz Erlangen', 'city': 'Erlangen'},
    {'country': GERMANY, 'name': 'Unitanz Göttingen', 'city': 'Göttingen'},
    {'country': GERMANY, 'name': 'Unitanz Hamburg', 'city': 'Hamburg'},
    {'country': GERMANY, 'name': 'Unitanz Hannover', 'city': 'Hannover'},
    {'country': GERMANY, 'name': 'Unitanz Hildesheim', 'city': 'Hildesheim'},
    {'country': GERMANY, 'name': 'Unitanz Kaiserslautern', 'city': 'Kaiserslautern'},
    {'country': GERMANY, 'name': 'Unitanz Karlsruhe', 'city': 'Karlsruhe'},
    {'country': GERMANY, 'name': 'Unitanz Kiel', 'city': 'Kiel'},
    {'country': GERMANY, 'name': 'Unitanz Mainz', 'city': 'Mainz'},
    {'country': GERMANY, 'name': 'Unitanz Mannheim', 'city': 'Mannheim'},
    {'country': GERMANY, 'name': 'Unitanz München', 'city': 'München'},
    {'country': GERMANY, 'name': 'Unitanz Münster', 'city': 'Münster'},
    {'country': GERMANY, 'name': 'Unitanz Rostock', 'city': 'Rostock'},
    {'country': GERMANY, 'name': 'Unitanz Stuttgart', 'city': 'Stuttgart'},
    {'country': GERMANY, 'name': 'Unitanz Trondheim', 'city': 'Trondheim'},
    {'country': GERMANY, 'name': 'Unitanz Ulm', 'city': 'Ulm'},
    {'country': GERMANY, 'name': 'Unitanz Winterthur', 'city': 'Winterthur'},
    {'country': GERMANY, 'name': 'Unitanz Wuppertal', 'city': 'Wuppertal'},
    {'country': BELGIUM, 'name': 'Gent', 'city': 'Gent'},
    {'country': CZECH, 'name': 'Brno', 'city': 'Brno'},
    {'country': NORWAY, 'name': 'Oslo', 'city': 'Oslo'},
    {'country': POLAND, 'name': 'Lublin', 'city': 'Lublin'},
    {'country': UNITED_KINGDOM, 'name': 'Hull', 'city': 'Hull'},
    {'country': UNITED_KINGDOM, 'name': 'Liverpool', 'city': 'Liverpool'}
]

raffle_config_items = [MAX_DANCERS, SELECTION_BUFFER]

# Registration form lists
LEVELS = {
    CHOOSE: 'What level are you dancing?',
    NO: 'Not dancing',
}
LEVELS.update({pl: ALL_LEVELS[pl] for pl in PARTICIPATING_LEVELS})
ROLES = {NONE: 'What role are you dancing?'}
ROLES.update(ALL_ROLES)
VOLUNTEER = {CHOOSE: 'Would you like to volunteer at the tournament?'}
VOLUNTEER.update(YMN)
FIRST_AID = {NONE: 'Are you a qualified First Aid Officer and would you like to volunteer as one?'}
FIRST_AID.update(YMN)
JURY_BALLROOM = {NONE: 'Would you like to volunteer as a Ballroom adjudicator?'}
JURY_BALLROOM.update(YMN)
JURY_LATIN = {NONE: 'Would you like to volunteer as a Latin adjudicator?'}
JURY_LATIN.update(YMN)
LICENSES = {
    NO: 'No, I do not have a license',
    'D': 'Yes, D',
    'C': 'Yes, C',
    'B': 'Yes, B',
    'A': 'Yes, A',
    'S': 'Yes, S'
}
LICENSE_BALLROOM = {'': 'Do you have an adjudicator license for Ballroom?'}
LICENSE_BALLROOM.update(LICENSES)
LICENSE_LATIN = {'': 'Do you have an adjudicator license for Latin?'}
LICENSE_LATIN.update(LICENSES)
JURY_SALSA = {'': 'Would you like to volunteer as a Salsa adjudicator?'}
JURY_SALSA.update(YMN)
JURY_POLKA = {'': 'Would you like to volunteer as a Polka adjudicator?'}
JURY_POLKA.update(YMN)
STUDENT = {'': 'Are you a student?'}
STUDENT.update(YN)
SLEEPING = {'': 'Would you like to stay in the sleeping halls?'}
SLEEPING.update(YN)
FIRST_TIME = {'': 'Is this your first time participating in {prefix} {tournament}?'.format(
    tournament=tournament_settings['tournament'], prefix='a' if tournament_settings['tournament'] == NTDS else 'an')}
FIRST_TIME.update(YN)
SHIRTS = {'': 'Would you like to buy a t-shirt from this tournament?', NO: 'No'}
SHIRTS.update({k: 'Yes, '+v for k, v in SHIRT_SIZES.items()})


# Format number to display as price
def euros(amount):
    return '€{:,.2f}'.format(amount/100)


# Prices for
PRICES = {'student': {True: STUDENT_PRICE, False: NON_STUDENT_PRICE},
          't-shirt': dict({NO: 0}, **{k: SHIRT_PRICE for k, v in SHIRT_SIZES.items()}),
          'stickers': STICKER_PRICE}


def finances_overview(dancers):
    students = [PRICES['student'][dancer.contestant_info[0].student] for dancer in dancers if
                dancer.contestant_info[0].student]
    non_students = [PRICES['student'][dancer.contestant_info[0].student] for dancer in dancers if not
                    dancer.contestant_info[0].student]
    shirts = [PRICES['t-shirt'][dancer.additional_info[0].t_shirt] for dancer in dancers if
              dancer.additional_info[0].t_shirt != NO]
    students_paid = [PRICES['student'][dancer.contestant_info[0].student] for dancer in dancers if
                     dancer.contestant_info[0].student and dancer.status_info[0].paid is True]
    non_students_paid = [PRICES['student'][dancer.contestant_info[0].student] for dancer in dancers if not
                         dancer.contestant_info[0].student and dancer.status_info[0].paid is True]
    shirts_paid = [PRICES['t-shirt'][dancer.additional_info[0].t_shirt] for dancer in dancers if
                   dancer.additional_info[0].t_shirt != NO and dancer.status_info[0].paid is True]
    stickers = [dancer.merchandise_info for dancer in dancers if len(dancer.merchandise_info) > 0]
    number_of_stickers = 0
    for merch in stickers:
        number_of_stickers += sum([m.quantity for m in merch])
    stickers = [dancer.merchandise_info for dancer in dancers if
                len(dancer.merchandise_info) > 0 and dancer.status_info[0].paid is True]
    number_of_paid_stickers = 0
    for merch in stickers:
        number_of_paid_stickers += sum([m.quantity for m in merch])
    return {'number_of_students': len(students), 'number_of_non_students': len(non_students), 't-shirts': len(shirts),
            'stickers': number_of_stickers,
            'price_students': sum(students), 'price_non_students': sum(non_students), 'price_t-shirts': sum(shirts),
            'price_stickers': number_of_stickers*PRICES['stickers'],
            'price_total': sum(students) + sum(non_students) + sum(shirts) + number_of_stickers*PRICES['stickers'],
            'number_of_students_paid': len(students_paid), 'number_of_non_students_paid': len(non_students_paid),
            't-shirts_paid': len(shirts_paid), 'stickers_paid': number_of_paid_stickers,
            'price_students_paid': sum(students_paid), 'price_non_students_paid': sum(non_students_paid),
            'price_t-shirts_paid': sum(shirts_paid), 'price_stickers_paid': number_of_paid_stickers*PRICES['stickers'],
            'price_total_paid': sum(students_paid + non_students_paid +
                                    shirts_paid) + number_of_paid_stickers*PRICES['stickers'],
            'total_number_of_payments': len(students) + len(non_students),
            'total_number_of_payments_paid': len(students_paid) + len(non_students_paid)
            }
