from ntds_webportal.tournament_config import *

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
    {'country': NORWAY, 'name': 'Oslo', 'city': 'Oslo'}
]

# Registration form lists
LEVELS = {
    CHOOSE: 'What level are you dancing?',
    NO: 'I am not dancing in this category',
}
LEVELS.update({pl: ALL_LEVELS[pl] for pl in PARTICIPATING_LEVELS})
ROLES = {NONE: 'What role are you dancing?'}
ROLES.update(ALL_ROLES)
VOLUNTEER = {CHOOSE: 'Would you like to volunteer at the tournament?'}
VOLUNTEER.update(YMN)
FIRST_AID = {NONE: 'Are you a qualified First Aid Officer and would you like to volunteer as one?'}
FIRST_AID.update(YMN)
JURY_BALLROOM = {NONE: 'Would you like to volunteer as a Ballroom jury?'}
JURY_BALLROOM.update(YMN)
JURY_LATIN = {NONE: 'Would you like to volunteer as a Latin jury?'}
JURY_LATIN.update(YMN)
SHIRTS = {'': 'Would you like to buy a t-shirt from this tournament?', NO: 'No'}
SHIRTS.update(SHIRT_SIZES)


# Format number to display as price
def euros(amount):
    return '€{:,.2f}'.format(amount/100)


# Prices for
PRICES = {'student': {True: STUDENT_PRICE, False: NON_STUDENT_PRICE},
          't-shirt': dict({NO: 0}, **{k: SHIRT_PRICE for k, v in SHIRT_SIZES.items()})}


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
    return {'number_of_students': len(students), 'number_of_non_students': len(non_students), 't-shirts': len(shirts),
            'price_students': sum(students), 'price_non_students': sum(non_students), 'price_t-shirts': sum(shirts),
            'price_total': sum(students) + sum(non_students) + sum(shirts),
            'number_of_students_paid': len(students_paid), 'number_of_non_students_paid': len(non_students_paid),
            't-shirts_paid': len(shirts_paid), 'price_students_paid': sum(students_paid),
            'price_non_students_paid': sum(non_students_paid), 'price_t-shirts_paid': sum(shirts_paid),
            'price_total_paid': sum(students_paid) + sum(non_students_paid) + sum(shirts_paid),
            'total_number_of_payments': len(students) + len(non_students),
            'total_number_of_payments_paid': len(students_paid) + len(non_students_paid)
            }
