from ntds_webportal import create_app, db
from ntds_webportal.models import User
from sqlalchemy_utils import database_exists, create_database
import sqlalchemy as alchemy


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


def build_sample_db():
    """
    Populate a small db with some example entries.
    """
    db.create_all()
    admin = User()
    admin.username = 'admin'
    admin.email = 'admin@admin.com'
    admin.set_password('admin')
    db.session.add(admin)
    db.session.commit()


def database_is_empty():
    table_names = alchemy.inspect(db.engine).get_table_names()
    is_empty = table_names == []
    print('Database empty: {is_empty}.'.format(is_empty=is_empty))
    return is_empty


if __name__ == '__main__':

    with app.app_context():
        if not database_exists(db.engine.url):
            create_database(db.engine.url)
        if database_is_empty():
            db.create_all()
            build_sample_db()

    app.run()
