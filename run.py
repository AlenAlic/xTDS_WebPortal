from ntds_webportal import create_app
from instance.populate import create_admin, create_organization, create_teams


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'prod': ProductionShell}


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
    app.run()
