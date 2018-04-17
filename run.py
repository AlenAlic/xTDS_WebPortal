from ntds_webportal import create_app, db
from sqlalchemy_utils import database_exists, create_database
import sqlalchemy as alchemy
from instance.populate import populate_db


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'populate': populate()}


def database_is_empty():
    table_names = alchemy.inspect(db.engine).get_table_names()
    is_empty = table_names == []
    print('Database empty: {is_empty}.'.format(is_empty=is_empty))
    return is_empty


def populate():
    with app.app_context():
        if not database_exists(db.engine.url):
            create_database(db.engine.url)
        if database_is_empty():
            db.create_all()
            populate_db()
            db.session.commit()


if __name__ == '__main__':

    populate()

    app.run()
