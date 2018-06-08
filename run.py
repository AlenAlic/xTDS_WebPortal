from ntds_webportal import create_app, db
from ntds_webportal.models import User, Notification, EXCLUDED_FROM_CLEARING, TeamFinances
import sqlalchemy as alchemy
from instance.populate import populate_test_db, create_users, create_tournament


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'dev': DevShell, 'prod': ProductionShell, 'User': User, 'Notification': Notification}


def database_is_empty():
    table_names = alchemy.inspect(db.engine).get_table_names()
    is_empty = table_names == []
    print('Database empty: {is_empty}.'.format(is_empty=is_empty))
    return is_empty


class ProductionShell:
    @staticmethod
    def create():
        with app.app_context():
            print('Creating Users.')
            create_users()
            create_tournament()


class DevShell:
    @staticmethod
    def create():
        with app.app_context():
            print('Creating Users.')
            create_users()
            create_tournament()

    @staticmethod
    def populate_test():
        with app.app_context():
            print('Populating with test data.')
            populate_test_db()

    @staticmethod
    def clear():
        with app.app_context():
            meta = db.metadata
            for table in reversed(meta.sorted_tables):
                if table.name not in EXCLUDED_FROM_CLEARING:
                    print('Cleared table {}.'.format(table))
                    db.session.execute(table.delete())
                    db.session.execute(f"ALTER TABLE {table.name} AUTO_INCREMENT = 1;")
            tf = TeamFinances.query.all()
            for f in tf:
                f.paid = 0
            create_tournament()
            db.session.commit()

    @staticmethod
    def full_clear():
        with app.app_context():
            meta = db.metadata
            for table in reversed(meta.sorted_tables):
                print('Cleared table {}.'.format(table))
                db.session.execute(table.delete())
                db.session.execute(f"ALTER TABLE {table.name} AUTO_INCREMENT = 1;")
            db.session.commit()

    def reset_test_data(self):
        with app.app_context():
            self.full_clear()
            self.create()
            self.populate_test()


if __name__ == '__main__':
    app.run()
