from flask import g, flash
from flask_login import current_user, logout_user
from ntds_webportal import create_app, db
from ntds_webportal.models import User, SystemConfiguration, TournamentState, RaffleConfiguration
import sqlalchemy as alchemy
from instance.populate import create_admin, create_organization, create_teams
import ntds_webportal.data as data


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'prod': ProductionShell, 'User': User}


@app.before_request
def before_request_callback():
    g.sc = SystemConfiguration.query.first()
    if not g.sc.website_accessible:
        if current_user.is_authenticated:
            if current_user.access > 0:
                logout_user()
                flash('The xTDS WebPortal is currently undergoing maintenance. '
                      'You have been logged out of you previous session.')
    g.data = data
    g.ts = TournamentState.query.first()
    g.rc = RaffleConfiguration.query.first()


def database_is_empty():
    table_names = alchemy.inspect(db.engine).get_table_names()
    is_empty = table_names == []
    print('Database empty: {is_empty}.'.format(is_empty=is_empty))
    return is_empty


def create_tournament_state_table():
    if len(TournamentState.query.all()) == 0:
        ts = TournamentState()
        db.session.add(ts)
        db.session.commit()


def create_system_configuration_table():
    if len(SystemConfiguration.query.all()) == 0:
        sc = SystemConfiguration()
        db.session.add(sc)
        db.session.commit()


def create_raffle_configuration_table():
    if len(RaffleConfiguration.query.all()) == 0:
        rc = RaffleConfiguration()
        db.session.add(rc)
        db.session.commit()


def prepare_site():
    with app.app_context():
        create_tournament_state_table()
        create_system_configuration_table()
        create_raffle_configuration_table()


class ProductionShell:

    def create(self):
        with app.app_context():
            self.create_admin()
            self.create_organization()
            self.create_teams()

    @staticmethod
    def create_admin():
        with app.app_context():
            print('Creating Admin.')
            create_admin()

    @staticmethod
    def create_organization():
        with app.app_context():
            print('Creating Organization.')
            create_organization()

    @staticmethod
    def create_teams():
        with app.app_context():
            print('Creating Teamcaptains and Treasurers.')
            create_teams()


if __name__ == '__main__':
    prepare_site()
    app.run()
