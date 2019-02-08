# Environments
DEVELOPMENT_ENV = 'development'
DEBUG_ENV = 'debug'
TESTING_ENV = 'testing'
PRODUCTION_ENV = 'production'
TESTING_ENVIRONMENTS = [DEVELOPMENT_ENV, TESTING_ENV, DEBUG_ENV]

# METHODS
GET = "GET"
POST = "POST"
PUT = "PUT"
PATCH = "PATCH"

# ACCESS
ADMIN = 'admin'
ORGANIZER = 'organizer'
BLIND_DATE_ASSISTANT = 'blind_date_assistant'
CHECK_IN_ASSISTANT = 'check_in_assistant'
ADJUDICATOR_ASSISTANT = 'adjudicator_assistant'
TOURNAMENT_OFFICE_MANAGER = 'tournament_office_manager'
FLOOR_MANAGER = 'floor_manager'
TEAM_CAPTAIN = 'team_captain'
TREASURER = 'treasurer'
DANCER = 'dancer'
SUPER_VOLUNTEER = 'super_volunteer'
ACCESS_LEVELS = {
    ADMIN: 'Admin',
    ORGANIZER: 'Tournament organizer',
    BLIND_DATE_ASSISTANT: 'Blind Date assistant',
    CHECK_IN_ASSISTANT: 'Check-in assistant',
    ADJUDICATOR_ASSISTANT: 'Adjudicator assistant',
    TOURNAMENT_OFFICE_MANAGER: 'Tournament office manager',
    FLOOR_MANAGER: 'Floor manager',
    TEAM_CAPTAIN: 'Team captain',
    TREASURER: 'Treasurer',
    DANCER: 'Dancer',
    SUPER_VOLUNTEER: 'Super Volunteer',
}

# Account Names
BLIND_DATE_ASSISTANT_ACCOUNT_NAME = 'BlindDateAssistant'
CHECK_IN_ASSISTANT_ACCOUNT_NAME = 'CheckInAssistant'
ADJUDICATOR_ASSISTANT_ACCOUNT_NAME = 'AdjudicatorAssistant'
TOURNAMENT_OFFICE_MANAGER_ACCOUNT_NAME = 'TournamentOfficeManager'
FLOOR_MANAGER_ACCOUNT_NAME = 'FloorManager'

#  Tournaments
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
COUNTRIES = [NETHERLANDS, GERMANY, BELGIUM, CZECH, NORWAY, UNITED_KINGDOM, POLAND]

# Cities
ENSCHEDE = 'Enschede'
AMSTERDAM = 'Amsterdam'
DELFT = 'Delft'
NIJMEGEN = 'Nijmegen'
ROTTERDAM = 'Rotterdam'
EINDHOVEN = 'Eindhoven'
LEIDEN = 'Leiden'
MAASTRICHT = 'Maastricht'
GRONINGEN = 'Groningen'
UTRECHT = 'Utrecht'
WAGENINGEN = 'Wageningen'
AACHEN = 'Aachen'
ANTIBES = 'Antibes'
BERLIN = 'Berlin'
BIELEFELD = 'Bielefeld'
BONN = 'Bonn'
CLAUSTHAL = 'Clausthal'
COTTBUS = 'Cottbus'
DARMSTADT = 'Darmstadt'
DORTMUND = 'Dortmund'
DUSSELDORF = 'Düsseldorf'
ERLANGEN = 'Erlangen'
GOTTINGEN = 'Göttingen'
HAMBURG = 'Hamburg'
HANNOVER = 'Hannover'
HILDESHEIM = 'Hildesheim'
KAISERSLAUTERN = 'Kaiserslautern'
KARLSRUHE = 'Karlsruhe'
KIEL = 'Kiel'
MAINZ = 'Mainz'
MANNHEIM = 'Mannheim'
MUNCHEN = 'München'
MUNSTER = 'Münster'
ROSTOCK = 'Rostock'
STUTTGART = 'Stuttgart'
TRONDHEIM = 'Trondheim'
ULM = 'Ulm'
WINTERTHUR = 'Winterthur'
WUPPERTAL = 'Wuppertal'
GENT = 'Gent'
BRNO = 'Brno'
OSLO = 'Oslo'
LUBLIN = 'Lublin'
HULL = 'Hull'
LIVERPOOL = 'Liverpool'
CITIES = [
    ENSCHEDE, AMSTERDAM, DELFT, NIJMEGEN, ROTTERDAM, EINDHOVEN, LEIDEN, MAASTRICHT, GRONINGEN, UTRECHT,
    WAGENINGEN, AACHEN, ANTIBES, BERLIN, BIELEFELD, BONN, CLAUSTHAL, COTTBUS, DARMSTADT, DORTMUND, DUSSELDORF,
    ERLANGEN, GOTTINGEN, HAMBURG, HANNOVER, HILDESHEIM, KAISERSLAUTERN, KARLSRUHE, KIEL, MAINZ, MANNHEIM, MUNCHEN,
    MUNSTER, ROSTOCK, STUTTGART, TRONDHEIM, ULM, WINTERTHUR, WUPPERTAL, GENT, BRNO, OSLO, LUBLIN, HULL, LIVERPOOL
]
CITIES.sort()
TEAM_SUPER_VOLUNTEER = "Super Volunteer"
TEAM_ORGANIZATION = "Organization"

# Basic options
NONE = 'None'
CHOOSE = 'choose'
NO = 'No'
MAYBE = 'Maybe'
YES = 'Yes'
YMN = {YES: YES, MAYBE: MAYBE, NO: NO}
YN = {str(True): YMN[YES], str(False): YMN[NO]}
TF = {True: YMN[YES], False: YMN[NO]}
YMN_CHOICES = [(YES, YES), (MAYBE, MAYBE), (NO, NO)]
DIET_ALLERGIES_DISPLAY = {None: '-'}
DIFF = 'diff'
STUDENT = 'student'
NON_STUDENT = 'non-student'
PHD_STUDENT = 'phd-student'
DEFAULT_STUDENT_PRICE = 5000
DEFAULT_NON_STUDENT_PRICE = 6000
DEFAULT_PHD_STUDENT_PRICE = 5500
STUDENT_TEXT = {STUDENT: 'Student', NON_STUDENT: NO, PHD_STUDENT: 'PhD-student'}
BAG = 'bag'
MUG = 'mug'
FIRST_TIME = 'first_time'
STUDENT_STRING = {STUDENT: 'Student', NON_STUDENT: 'Non-student', PHD_STUDENT: 'PhD-student'}

# Categories
COMPETITION = 'competition'
BALLROOM = 'Ballroom'
LATIN = 'Latin'
SALSA = 'Salsa'
POLKA = 'Polka'
ALL_COMPETITIONS = [BALLROOM, LATIN]
COMPETITION_CHOICE = {"": "Choose a competition", BALLROOM: BALLROOM, LATIN: LATIN}

# All available levels
LEVEL = 'level'
TEST = 'TEST'
BEGINNERS = 'Beginners'
BREITENSPORT = 'Breitensport'
AMATEURS = 'Amateurs'
PROFESSIONALS = 'Professionals'
MASTERS = 'Masters'
CHAMPIONS = 'Champions'
CLOSED = "CloseD"
OPEN_CLASS = "Open Class"
NOT_DANCING = 'Not dancing'
LEVELS_SORT_ORDER = {BEGINNERS: 0, BREITENSPORT: 1, CLOSED: 2, OPEN_CLASS: 3, NO: 4}
LIONS = 'Lions'

# Dancing roles
BOTH = 'Both'
ROLE = 'role'
LEAD = 'Lead'
FOLLOW = 'Follow'
ALL_ROLES = [LEAD, FOLLOW]
ROLES_FORM = {
    LEAD: LEAD,
    FOLLOW: FOLLOW
}
OPPOSITE_ROLES = {LEAD: FOLLOW, FOLLOW: LEAD}
LEVEL_ROLE_DISPLAY = {NO: "-", BEGINNERS: BEGINNERS, BREITENSPORT: BREITENSPORT, CLOSED: CLOSED, OPEN_CLASS: OPEN_CLASS,
                      LEAD: LEAD, FOLLOW: FOLLOW}

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
NO_GDPR = 'no_gdpr'
STATUS = {
    REGISTERED: 'Registered',
    SELECTED: 'Selected',
    CONFIRMED: 'Confirmed',
    CANCELLED: 'Cancelled',
    NO_GDPR: 'Not accepted GDPR'
}

# T-shirt sizes
SHIRT_SIZES = {
    'MS': 'Men\'s S',
    'MM': 'Men\'s M',
    'ML': 'Men\'s L',
    'MXL': 'Men\'s XL',
    'MXXL': 'Men\'s XXL',
    'FXS': 'Woman\'s XS',
    'FS': 'Woman\'s S',
    'FM': 'Woman\'s M',
    'FL': 'Woman\'s L',
    'FXL': 'Woman\'s XL',
    'FXXL': 'Woman\'s XXL'
}

# Website state warnings
ORGANIZERS_NOTIFIED = 1
SYSTEM_CONFIGURED = 2
TEAM_CAPTAINS_HAVE_ACCESS = 3
REGISTRATION_STARTED = 4
REGISTRATION_CLOSED = 5
REGISTRATION_OPEN = 6
RAFFLE_COMPLETED = 7
RAFFLE_CONFIRMED = 8

WEBSITE_NOT_CONFIGURED_TEXT = "Cannot enter page. Please configure the xTDS WebPortal first."
TEAM_CAPTAINS_DO_NOT_HAVE_ACCESS_TEXT = "Cannot enter page. This page will be accessible after the team captain " \
                                        "accounts have been activated."
REGISTRATION_NOT_STARTED_TEXT = "Cannot enter page. " \
                                "This page will be accessible after the registration period has started."
REGISTRATION_NOT_OPEN_TEXT = "Registration is currently closed."
RAFFLE_NOT_CONFIRMED_TEXT = "Cannot enter page. This page will be accessible after the raffle has taken place."

# Dances
SLOW_WALTZ = "Slow Waltz"
TANGO = "Tango"
VIENNESE_WALTZ = "Viennese Waltz"
SLOW_FOXTROT = "Slow Foxtrot"
QUICKSTEP = "Quickstep"
SAMBA = "Samba"
CHA_CHA_CHA = "Cha Cha Cha"
RUMBA = "Rumba"
PASO_DOBLE = "Paso Doble"
JIVE = "Jive"
DANCES = [
    {"name": SLOW_WALTZ, "tag": "SW"},
    {"name": TANGO, "tag": "TG"},
    {"name": VIENNESE_WALTZ, "tag": "VW"},
    {"name": SLOW_FOXTROT, "tag": "SF"},
    {"name": QUICKSTEP, "tag": "QS"},
    {"name": SAMBA, "tag": "SB"},
    {"name": CHA_CHA_CHA, "tag": "CC"},
    {"name": RUMBA, "tag": "RB"},
    {"name": PASO_DOBLE, "tag": "PD"},
    {"name": JIVE, "tag": "JV"},
]
# Basic dances and order
BALLROOM_DANCES = [SLOW_WALTZ, TANGO, VIENNESE_WALTZ, SLOW_FOXTROT, QUICKSTEP]
BALLROOM_BASIC_DANCES = [SLOW_WALTZ, TANGO, QUICKSTEP]
BALLROOM_DANCE_ORDER = {SLOW_WALTZ: 0, TANGO: 1, VIENNESE_WALTZ: 2, SLOW_FOXTROT: 3, QUICKSTEP: 4}
LATIN_DANCES = [SAMBA, CHA_CHA_CHA, RUMBA, PASO_DOBLE, JIVE]
LATIN_BASIC_DANCES = [CHA_CHA_CHA, RUMBA, JIVE]
LATIN_DANCE_ORDER = {SAMBA: 0, CHA_CHA_CHA: 1, RUMBA: 2, PASO_DOBLE: 3, JIVE: 4}
BASIC_DANCES = {BALLROOM: BALLROOM_BASIC_DANCES, LATIN: LATIN_BASIC_DANCES}
DANCE_ORDER = {BALLROOM: BALLROOM_DANCE_ORDER, LATIN: LATIN_DANCE_ORDER}

# Classes
BREITENSPORT_QUALIFICATION = BREITENSPORT + ' (Qualification)'
DANCING_CLASSES = [
    TEST,
    BEGINNERS,
    BREITENSPORT_QUALIFICATION,
    AMATEURS,
    PROFESSIONALS,
    MASTERS,
    CHAMPIONS,
    CLOSED,
    OPEN_CLASS
]
BREITENSPORT_COMPETITIONS = [AMATEURS, PROFESSIONALS, MASTERS, CHAMPIONS]
BREITENSPORT_ORDER = {AMATEURS: 0, PROFESSIONALS: 1, MASTERS: 2, CHAMPIONS: 3}
# Classes short names
SHORT_REPRESENTATIONS = {
    TEST: TEST,
    BEGINNERS: BEGINNERS[:3],
    BREITENSPORT_QUALIFICATION: BREITENSPORT_QUALIFICATION[:2],
    AMATEURS: AMATEURS[:3],
    PROFESSIONALS: PROFESSIONALS[:4],
    MASTERS: MASTERS[:2],
    CHAMPIONS: CHAMPIONS[:2],
    CLOSED: CLOSED[:2],
    OPEN_CLASS: 'OC',
    BALLROOM: BALLROOM[:2],
    LATIN: LATIN[:2],
    SALSA: SALSA,
    POLKA: POLKA,
}
