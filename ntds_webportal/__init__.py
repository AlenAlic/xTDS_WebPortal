from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
admin = Admin(template_mode='bootstrap3')


class BaseView(ModelView):
    column_hide_backrefs = True
    page_size = 50

    def is_accessible(self):
        return current_user.is_admin()


class UserView(BaseView):
    column_exclude_list = ['password_hash', ]
    form_excluded_columns = ['password_hash', ]
    form_extra_fields = {'password2': PasswordField('Password')}

    def on_model_change(self, form, User, is_created):
        if form.password2.data is not None:
            User.set_password(form.password2.data)


def create_app():
    """
    Create instance of website.
    """
    from ntds_webportal.models import User, Team, Contestant, ContestantInfo, DancingInfo, VolunteerInfo,\
        AdditionalInfo, StatusInfo

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'main.index'
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    admin.init_app(app)
    admin.add_view(UserView(User, db.session))
    admin.add_view(BaseView(Team, db.session))
    admin.add_view(BaseView(Contestant, db.session))
    admin.add_view(BaseView(ContestantInfo, db.session))
    admin.add_view(BaseView(DancingInfo, db.session))
    admin.add_view(BaseView(VolunteerInfo, db.session))
    admin.add_view(BaseView(AdditionalInfo, db.session))
    admin.add_view(BaseView(StatusInfo, db.session))

    from ntds_webportal.main import bp as main_bp
    app.register_blueprint(main_bp)

    from ntds_webportal.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from ntds_webportal.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from ntds_webportal.teamcaptains import bp as teamcaptains_bp
    app.register_blueprint(teamcaptains_bp, url_prefix='/teamcaptains')

    return app


from ntds_webportal import models
