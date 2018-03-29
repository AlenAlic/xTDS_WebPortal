# Countries
NETHERLANDS = 'The Netherlands'
GERMANY = 'Germany'
BELGIUM = 'Belgium'
CZECH = 'Czech Republic'
NORWAY = 'Norway'

# Basic options
NONE = 'None'
CHOOSE = 'choose'
NO = 'no'
MAYBE = 'maybe'
YES = 'yes'
YMN = {YES: 'Yes', MAYBE: 'Maybe', NO: 'No'}
TF = {True: YMN[YES], False: YMN[NO]}

# Categories
COMPETITION = 'competition'
BALLROOM = 'Ballroom'
LATIN = 'Latin'
ALL_COMPETITIONS = [BALLROOM, LATIN]

# All available levels
LEVEL = 'level'
BEGINNERS = 'Beginners'
BREITENSPORT = 'Breitensport'
CLOSED = 'CloseD'
OPEN_CLASS = 'Open Class'
ALL_LEVELS = {
    BEGINNERS: BEGINNERS,
    BREITENSPORT: BREITENSPORT,
    CLOSED: CLOSED,
    OPEN_CLASS: OPEN_CLASS
}

# Dancing roles
ROLE = 'role'
LEAD = 'lead'
FOLLOW = 'follow'
ALL_ROLES = {
    LEAD: 'Lead',
    FOLLOW: 'Follow'
}

# Status values
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
