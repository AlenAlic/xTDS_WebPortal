from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
moment = Moment()


def create_app():
    """
    Create instance of website.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'main.index'
    bootstrap.init_app(app)
    moment.init_app(app)

    from ntds_webportal.main import bp as main_bp
    app.register_blueprint(main_bp)

    from ntds_webportal.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app


from ntds_webportal import models
