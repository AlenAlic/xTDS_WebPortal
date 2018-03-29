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
BALLROOM = 'Ballroom'
LATIN = 'Latin'
ALL_CATEGORIES = [BALLROOM, LATIN]

# All available levels
BEGINNERS = 'beginners'
BREITENSPORT = 'breitensport'
CLOSED = 'closed'
OPEN_CLASS = 'open_class'
ALL_LEVELS = {
    BEGINNERS: 'Beginners',
    BREITENSPORT: 'Breitensport',
    CLOSED: 'CloseD',
    OPEN_CLASS: 'Open Class'
}

# Dancing roles
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
