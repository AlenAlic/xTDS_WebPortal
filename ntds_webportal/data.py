TEAMS = [
    {'name': '4 happy feet', 'city': 'Enschede'},
    {'name': 'AmsterDance', 'city': 'Amsterdam',},
    {'name': 'Blue Suede Shoes', 'city': 'Delft'},
    {'name': 'Dance Fever', 'city': 'Nijmegen'},
    {'name': 'Erasmus Dance Society', 'city': 'Rotterdam'},
    {'name': 'Footloose', 'city': 'Eindhoven'},
    {'name': 'LeiDance', 'city': 'Leiden'},
    {'name': 'Let`s Dance', 'city': 'Maastricht'},
    {'name': 'The Blue Toes', 'city': 'Groningen'},
    {'name': 'U Dance', 'city': 'Utrecht'},
    {'name': 'WUBDA', 'city': 'Wageningen'}
]

ACCESS = {
    'admin': 0,
    'organizer': 1,
    'blind_date_organizer': 2,
    'team_captain': 3,
    'treasurer': 4
}

NONE = 'None'
CHOOSE = 'choose'
NO = 'no'
MAYBE = 'maybe'
YES = 'yes'
YMN = {YES: 'Yes', MAYBE: 'Maybe', NO: 'No'}
TF = {True: YMN[YES], False: YMN[NO]}

BEGINNERS = 'beginners'
BREITENSPORT = 'breitensport'
CLOSED = 'closed'
OPEN_CLASS = 'open_class'
LEVELS = {
    CHOOSE: 'What level are you dancing?',
    NO: 'I am not dancing in this category',
    BREITENSPORT: 'Breitensport',
    CLOSED: 'CloseD',
    OPEN_CLASS: 'Open Class'
}

LEAD = 'lead'
FOLLOW = 'follow'
ROLES = {
    NONE: 'What role are you dancing?',
    LEAD: 'Lead',
    FOLLOW: 'Follow'
}

VOLUNTEER = {CHOOSE: 'Would you like to volunteer at the tournament?'}
VOLUNTEER.update(YMN)
FIRST_AID = {NONE: 'Are you a qualified First Aid Officer and would you like to volunteer as one?'}
FIRST_AID.update(YMN)
JURY_BALLROOM = {NONE: 'Would you like to volunteer as a Ballroom jury?'}
JURY_BALLROOM.update(YMN)
JURY_LATIN = {NONE: 'Would you like to volunteer as a Latin jury?'}
JURY_LATIN.update(YMN)

SHIRT_SIZES = {
    'MS': 'Men\'s S',
    'MM': 'Men\'s M',
    'ML': 'Men\'s L',
    'MXL': 'Men\'s XL',
    'FS': 'Woman\'s S',
    'FM': 'Woman\'s M',
    'FL': 'Woman\'s L',
    'FXL': 'Woman\'s XL'
}
SHIRTS = {'': 'Would you like to buy a t-shirt from this tournament?', NO: 'No'}
SHIRTS.update(SHIRT_SIZES)


REGISTERED = 'registered'
SELECTED = 'selected'
CONFIRMED = 'confirmed'
CANCELLED = 'cancelled'
STATUS = {
    REGISTERED: 'Registered',
    SELECTED: 'Selected',
    CONFIRMED: 'Confirmed',
    CANCELLED: 'Cancelled'
}


def euros(cents):
    return '€{:,.2f}'.format(cents/100)


STUDENT_PRICE = 7000
NON_STUDENT_PRICE = 8000
SHIRT_PRICE = 1500
PRICES = {'entry_fee': {True: STUDENT_PRICE, False: NON_STUDENT_PRICE},
          't-shirt': dict({NO: 0}, **{k: SHIRT_PRICE for k, v in SHIRT_SIZES.items()})}


def finances_overview(dancers):
    students = [PRICES['entry_fee'][dancer.contestant_info[0].student] for dancer in dancers if
                dancer.contestant_info[0].student]
    non_students = [PRICES['entry_fee'][dancer.contestant_info[0].student] for dancer in dancers if not
                dancer.contestant_info[0].student]
    shirts = [PRICES['t-shirt'][dancer.additional_info[0].t_shirt] for dancer in dancers if
              dancer.additional_info[0].t_shirt != NO]
    return {'number_of_students': len(students), 'number_of_non_students': len(non_students), 't-shirts': len(shirts),
            'price_students': sum(students), 'price_non_students': sum(non_students), 'price_t-shirts': sum(shirts),
            'price_total': sum(students) + sum(non_students) + sum(shirts)}
