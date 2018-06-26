# Tournaments
NTDS = 'NTDS'
ETDS = 'ETDS'

# Countries
NETHERLANDS = 'The Netherlands'
GERMANY = 'Germany'
BELGIUM = 'Belgium'
CZECH = 'Czech Republic'
NORWAY = 'Norway'
UNITED_KINGDOM = 'United Kingdom'
POLAND = 'Poland'

# Basic options
NONE = 'None'
CHOOSE = 'choose'
NO = 'no'
MAYBE = 'maybe'
YES = 'yes'
YMN = {YES: 'Yes', MAYBE: 'Maybe', NO: 'No'}
YN = {str(True): YMN[YES], str(False): YMN[NO]}
TF = {True: YMN[YES], False: YMN[NO]}
DIFF = 'diff'

# Categories
COMPETITION = 'competition'
BALLROOM = 'Ballroom'
LATIN = 'Latin'
SALSA = 'Salsa'
POLKA = 'Polka'
ALL_COMPETITIONS = [BALLROOM, LATIN]

# All available levels
LEVEL = 'level'
BEGINNERS = 'Beginners'
BREITENSPORT = 'Breitensport'
CLOSED = "CloseD"
OPEN_CLASS = "Open Class"
ALL_LEVELS = {
    BEGINNERS: BEGINNERS,
    BREITENSPORT: BREITENSPORT,
    CLOSED: CLOSED,
    OPEN_CLASS: OPEN_CLASS
}

# Dancing roles
ROLE = 'role'
LEAD = 'Lead'
FOLLOW = 'Follow'
ALL_ROLES = {
    LEAD: LEAD,
    FOLLOW: FOLLOW
}

# Competition levels
BELOW_D = 'Below D'
D_LEVEL = 'D'
C_LEVEL = 'C'
B_LEVEL = 'B'
A_LEVEL = 'A'
S_LEVEL = 'S'
COMPETITION_LEVELS = {
    D_LEVEL: D_LEVEL,
    C_LEVEL: C_LEVEL,
    B_LEVEL: B_LEVEL,
    A_LEVEL: A_LEVEL,
    S_LEVEL: S_LEVEL
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
