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

CHOOSE = 'choose'
BEGINNERS = 'beginners'
BREITENSPORT = 'breitensport'
CLOSED = 'closed'
OPEN_CLASS = 'open_class'
LEVELS = [
    (CHOOSE, 'What level are you dancing?'),
    ('no', 'I am not dancing in this category'),
    (BREITENSPORT, 'Breitensport'),
    (CLOSED, 'CloseD'),
    (OPEN_CLASS, 'Open Class')
]

LEAD = 'lead'
FOLLOW = 'follow'
ROLES = [
    ('None', 'What role are you dancing?'),
    ('no', 'I am not dancing in this category'),
    (LEAD, 'Lead'),
    (FOLLOW, 'Follow')
]

NO = 'no'
MAYBE = 'maybe'
YES = 'yes'
YMN = [
    (YES, 'Yes'),
    (MAYBE, 'Maybe'),
    (NO, 'No')
]

VOLUNTEER = [(CHOOSE, 'Would you like to volunteer at the tournament?')] + YMN
FIRST_AID = [('None', 'Are you a qualified First Aid Officer and would you like to volunteer as one?')] + YMN
JURY_BALLROOM = [('None', 'Would you like to volunteer as a Ballroom jury?')] + YMN
JURY_LATIN = [('None', 'Would you like to volunteer as a Latin jury?')] + YMN

SHIRTS = [
    ('', 'Would you like a t-shirt?'),
    ('no', 'No'),
    ('MS', 'Yes, Men\'s S'),
    ('MM', 'Yes, Men\'s M'),
    ('ML', 'Yes, Men\'s L'),
    ('MXL', 'Yes, Men\'s XL'),
    ('FS', 'Yes, Woman\'s S'),
    ('FM', 'Yes, Woman\'s M'),
    ('FL', 'Yes, Woman\'s L'),
    ('FXL', 'Yes, Woman\'s XL')
]
