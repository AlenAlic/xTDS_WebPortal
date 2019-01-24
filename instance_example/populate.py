from ntds_webportal import db
from ntds_webportal.models import User, Team
from ntds_webportal.data import *


TEAM_CAPTAINS = [
    {'team': '4 happy feet', 'country': 'The Netherlands', 'city': 'Enschede',
     'username': 'TeamcaptainEnschede', 'email': 'email@example.com', 'password': 'qwerty'},
]

TREASURERS = [{'city': t['city'], 'username': 'Treasurer' + t['city']} for t in TEAM_CAPTAINS]


def create_admin():
    admin = User()
    admin.username = 'admin'
    admin.email = 'email@example.com'
    admin.set_password('password')
    admin.access = ACCESS[ADMIN]
    admin.is_active = True
    db.session.add(admin)
    db.session.commit()


def create_organization():
    organisation = User()
    organisation.username = 'NTDSEnschede2018'
    organisation.email = 'email@example.com'
    organisation.set_password('password')
    organisation.access = ACCESS[ORGANIZER]
    organisation.is_active = True
    db.session.add(organisation)
    db.session.commit()


def create_teams():

    for value in TEAM_CAPTAINS:
        team = Team()
        team.country = value['country']
        team.city = value['city']
        team.name = value['team']
        db.session.add(team)
        tc = User()
        tc.username = value['username']
        tc.email = value['email']
        tc.set_password(value['password'])
        tc.access = ACCESS[TEAM_CAPTAIN]
        tc.is_active = True if value['email'] is not None else False
        tc.team = team
        db.session.add(tc)

    for value in TREASURERS:
        treasurer = User()
        treasurer.username = value['username']
        treasurer.access = ACCESS[TREASURER]
        treasurer.is_active = False
        treasurer.team = db.session.query(Team).filter_by(city=value['city']).first()
        db.session.add(treasurer)

    db.session.commit()
