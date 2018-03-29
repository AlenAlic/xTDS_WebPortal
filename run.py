from ntds_webportal import create_app, db
import sqlalchemy as alchemy
# noinspection PyPackageRequirements
from instance.populate import populate_test_db, create_users
from ntds_webportal.models import User, Notification

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'dev': DevShell, 'User': User, 'Notification': Notification}


def database_is_empty():
    table_names = alchemy.inspect(db.engine).get_table_names()
    is_empty = table_names == []
    print('Database empty: {is_empty}.'.format(is_empty=is_empty))
    return is_empty


class DevShell:
    @staticmethod
    def create():
        with app.app_context():
            print('Creating Users.')
            create_users()

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
                print('Cleared table {}.'.format(table))
                db.session.execute(table.delete())
            db.session.commit()

    @staticmethod
    def reset(self):
        self.clear()
        self.create()
        self.populate_test()


if __name__ == '__main__':
    app.run()
