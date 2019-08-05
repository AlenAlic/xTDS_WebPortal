from ntds_webportal.values import *

# Access levels
ACCESS = {
    ADMIN: 0,
    ORGANIZER: 1,
    BLIND_DATE_ASSISTANT: 2,
    CHECK_IN_ASSISTANT: 3,
    ADJUDICATOR_ASSISTANT: 4,
    TOURNAMENT_OFFICE_MANAGER: 5,
    FLOOR_MANAGER: 6,
    PRESENTER: 7,
    TEAM_CAPTAIN: 10,
    TREASURER: 11,
    DANCER: 12,
    SUPER_VOLUNTEER: 20
}
PROFILE_ACCESS = [ACCESS[ADMIN], ACCESS[ORGANIZER], ACCESS[TEAM_CAPTAIN], ACCESS[TREASURER], ACCESS[DANCER],
                  ACCESS[SUPER_VOLUNTEER]]
MESSAGES_ACCESS = [ACCESS[ADMIN], ACCESS[ORGANIZER], ACCESS[TEAM_CAPTAIN], ACCESS[TREASURER],
                   ACCESS[ADJUDICATOR_ASSISTANT]]

ASSISTANTS = {
    CHECK_IN_ASSISTANT_ACCOUNT_NAME: CHECK_IN_ASSISTANT,
    BLIND_DATE_ASSISTANT_ACCOUNT_NAME: BLIND_DATE_ASSISTANT,
    ADJUDICATOR_ASSISTANT_ACCOUNT_NAME: ADJUDICATOR_ASSISTANT,
    TOURNAMENT_OFFICE_MANAGER_ACCOUNT_NAME: TOURNAMENT_OFFICE_MANAGER,
    FLOOR_MANAGER_ACCOUNT_NAME: FLOOR_MANAGER
}

# All possible teams
TEAMS = [
    {'country': NETHERLANDS, 'name': '4 happy feet', 'city': ENSCHEDE},
    {'country': NETHERLANDS, 'name': 'AmsterDance', 'city': AMSTERDAM},
    {'country': NETHERLANDS, 'name': 'Blue Suede Shoes', 'city': DELFT},
    {'country': NETHERLANDS, 'name': 'Dance Fever', 'city': NIJMEGEN},
    {'country': NETHERLANDS, 'name': 'Erasmus Dance Society', 'city': ROTTERDAM},
    {'country': NETHERLANDS, 'name': 'Footloose', 'city': EINDHOVEN},
    {'country': NETHERLANDS, 'name': 'LeiDance', 'city': LEIDEN},
    {'country': NETHERLANDS, 'name': 'Let`s Dance', 'city': MAASTRICHT},
    {'country': NETHERLANDS, 'name': 'The Blue Toes', 'city': GRONINGEN},
    {'country': NETHERLANDS, 'name': 'U Dance', 'city': UTRECHT},
    {'country': NETHERLANDS, 'name': 'WuBDA', 'city': WAGENINGEN},
    {'country': GERMANY, 'name': 'Unitanz Aachen', 'city': AACHEN},
    {'country': GERMANY, 'name': 'Unitanz Antibes', 'city': ANTIBES},
    {'country': GERMANY, 'name': 'Unitanz Berlin', 'city': BERLIN},
    {'country': GERMANY, 'name': 'Unitanz Bielefeld', 'city': BIELEFELD},
    {'country': GERMANY, 'name': 'Unitanz Bonn', 'city': BONN},
    {'country': GERMANY, 'name': 'Unitanz Clausthal', 'city': CLAUSTHAL},
    {'country': GERMANY, 'name': 'Unitanz Cottbus', 'city': COTTBUS},
    {'country': GERMANY, 'name': 'Unitanz Darmstadt', 'city': DARMSTADT},
    {'country': GERMANY, 'name': 'Unitanz Dortmund', 'city': DORTMUND},
    {'country': GERMANY, 'name': 'Unitanz Düsseldorf', 'city': DUSSELDORF},
    {'country': GERMANY, 'name': 'Unitanz Erlangen', 'city': ERLANGEN},
    {'country': GERMANY, 'name': 'Unitanz Göttingen', 'city': GOTTINGEN},
    {'country': GERMANY, 'name': 'Unitanz Hamburg', 'city': HAMBURG},
    {'country': GERMANY, 'name': 'Unitanz Hannover', 'city': HANNOVER},
    {'country': GERMANY, 'name': 'Unitanz Hildesheim', 'city': HILDESHEIM},
    {'country': GERMANY, 'name': 'Unitanz Kaiserslautern', 'city': KAISERSLAUTERN},
    {'country': GERMANY, 'name': 'Unitanz Karlsruhe', 'city': KARLSRUHE},
    {'country': GERMANY, 'name': 'Unitanz Kiel', 'city': KIEL},
    {'country': GERMANY, 'name': 'Unitanz Mainz', 'city': MAINZ},
    {'country': GERMANY, 'name': 'Unitanz Mannheim', 'city': MANNHEIM},
    {'country': GERMANY, 'name': 'Unitanz München', 'city': MUNCHEN},
    {'country': GERMANY, 'name': 'Unitanz Münster', 'city': MUNSTER},
    {'country': GERMANY, 'name': 'Unitanz Rostock', 'city': ROSTOCK},
    {'country': GERMANY, 'name': 'Unitanz Stuttgart', 'city': STUTTGART},
    {'country': GERMANY, 'name': 'Unitanz Trondheim', 'city': TRONDHEIM},
    {'country': GERMANY, 'name': 'Unitanz Ulm', 'city': ULM},
    {'country': GERMANY, 'name': 'Unitanz Winterthur', 'city': WINTERTHUR},
    {'country': GERMANY, 'name': 'Unitanz Wuppertal', 'city': WUPPERTAL},
    {'country': BELGIUM, 'name': 'Gent', 'city': GENT},
    {'country': CZECH, 'name': 'Brno', 'city': BRNO},
    {'country': NORWAY, 'name': 'Oslo', 'city': OSLO},
    {'country': POLAND, 'name': 'Lublin', 'city': LUBLIN},
    {'country': UNITED_KINGDOM, 'name': 'Hull', 'city': HULL},
    {'country': UNITED_KINGDOM, 'name': 'Liverpool', 'city': LIVERPOOL}
]

# Registration form lists
ROLES = {NONE: 'What role are you dancing?'}
ROLES.update(ROLES_FORM)
ROLES.update({NO: 'I\'m not dancing'})
BLIND_DATE = {NONE: 'Do you have to Blind date in this category?'}
BLIND_DATE.update(YN)
VOLUNTEER_FORM = {CHOOSE: 'Would you like to volunteer at the tournament?'}
VOLUNTEER_FORM.update(YMN)
FIRST_AID = {NONE: 'Are you a qualified First Aid Officer and would you like to volunteer as one?'}
FIRST_AID.update(YMN)
EMERGENCY_RESPONSE_OFFICER = {NONE: 'Are you a qualified Emergency Response Officer and would you like to '
                                    'volunteer as one?'}
EMERGENCY_RESPONSE_OFFICER.update(YMN)
JURY_BALLROOM = {NONE: 'Would you like to volunteer as a Ballroom adjudicator?'}
JURY_BALLROOM.update(YMN)
JURY_LATIN = {NONE: 'Would you like to volunteer as a Latin adjudicator?'}
JURY_LATIN.update(YMN)
LICENSES = {NO: 'No, I do not have a license'}
LICENSES.update({k: 'Yes, '+v for k, v in COMPETITION_LEVELS.items()})
LICENSE_BALLROOM = {NONE: 'Do you have an adjudicator license for Ballroom?'}
LICENSE_BALLROOM.update(LICENSES)
LICENSE_LATIN = {NONE: 'Do you have an adjudicator license for Latin?'}
LICENSE_LATIN.update(LICENSES)
JURY_LEVELS = {BELOW_D: BELOW_D}
JURY_LEVELS.update(COMPETITION_LEVELS)
LEVEL_JURY_BALLROOM = {NONE: 'What is your highest achieved level in Ballroom?'}
LEVEL_JURY_BALLROOM.update(JURY_LEVELS)
LEVEL_JURY_LATIN = {NONE: 'What is your highest achieved level in Latin?'}
LEVEL_JURY_LATIN.update(JURY_LEVELS)
JURY_LEVELS_EDIT = {EMPTY: EMPTY}
JURY_LEVELS_EDIT.update(JURY_LEVELS)
LEVEL_JURY_BALLROOM_EDIT = {NONE: 'What is your highest achieved level in Ballroom?'}
LEVEL_JURY_BALLROOM_EDIT.update(JURY_LEVELS_EDIT)
LEVEL_JURY_LATIN_EDIT = {NONE: 'What is your highest achieved level in Latin?'}
LEVEL_JURY_LATIN_EDIT.update(JURY_LEVELS_EDIT)
JURY_SALSA = {NONE: 'Would you like to volunteer as a Salsa adjudicator?'}
JURY_SALSA.update(YMN)
JURY_POLKA = {NONE: 'Would you like to volunteer as a Polka adjudicator?'}
JURY_POLKA.update(YMN)
SLEEPING = {'': 'Would you like to stay in the sleeping halls?'}
SLEEPING.update(YN)


# Format number to display as price
def euros(amount):
    if amount != 0:
        return '€{:,.2f}'.format(amount/100)
    else:
        return '-'


def has_partner_display(partner_number, show_number=False):
    if partner_number is not None:
        if show_number:
            return partner_number
        else:
            return YES
    else:
        return "-"
