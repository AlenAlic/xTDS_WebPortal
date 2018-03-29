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

# Registration form lists
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
