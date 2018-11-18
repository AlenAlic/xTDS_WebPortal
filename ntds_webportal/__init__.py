from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_debugtoolbar import DebugToolbarExtension
from wtforms import PasswordField


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('main.index'))
        else:
            if current_user.is_admin():
                return self.render(self._template)
            else:
                return redirect(url_for('main.index'))


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
admin = Admin(template_mode='bootstrap3', index_view=MyAdminIndexView())
toolbar = DebugToolbarExtension()


class BaseView(ModelView):
    column_hide_backrefs = False
    page_size = 100

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_admin()
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index'))


class UserView(BaseView):
    column_exclude_list = ['password_hash', ]
    form_excluded_columns = ['password_hash', ]
    form_extra_fields = {'password2': PasswordField('Password')}

    # noinspection PyPep8Naming
    def on_model_change(self, form, User, is_created):
        if form.password2.data != '':
            User.set_password(form.password2.data)


def create_app():
    """
    Create instance of website.
    """
    from ntds_webportal.models import User, Team, Contestant, ContestantInfo, DancingInfo, StatusInfo, PaymentInfo, \
        VolunteerInfo, AdditionalInfo, MerchandiseInfo, Notification, PartnerRequest, NameChangeRequest, \
        TournamentState, SalsaPartners, PolkaPartners, SystemConfiguration, RaffleConfiguration, \
        AttendedPreviousTournamentContestant, NotSelectedContestant, SuperVolunteer

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:'))
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
    admin.add_view(BaseView(StatusInfo, db.session))
    admin.add_view(BaseView(PaymentInfo, db.session))
    admin.add_view(BaseView(VolunteerInfo, db.session))
    admin.add_view(BaseView(AdditionalInfo, db.session))
    admin.add_view(BaseView(MerchandiseInfo, db.session))
    admin.add_view(BaseView(Notification, db.session))
    admin.add_view(BaseView(PartnerRequest, db.session))
    admin.add_view(BaseView(NameChangeRequest, db.session))
    admin.add_view(BaseView(SalsaPartners, db.session))
    admin.add_view(BaseView(PolkaPartners, db.session))
    admin.add_view(BaseView(TournamentState, db.session))
    admin.add_view(BaseView(SystemConfiguration, db.session))
    admin.add_view(BaseView(RaffleConfiguration, db.session))
    admin.add_view(BaseView(AttendedPreviousTournamentContestant, db.session))
    admin.add_view(BaseView(NotSelectedContestant, db.session))
    admin.add_view(BaseView(SuperVolunteer, db.session))
    toolbar.init_app(app)

    from ntds_webportal.main import bp as main_bp
    app.register_blueprint(main_bp)

    from ntds_webportal.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from ntds_webportal.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from ntds_webportal.self_admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from ntds_webportal.teamcaptains import bp as teamcaptains_bp
    app.register_blueprint(teamcaptains_bp, url_prefix='/teamcaptains')

    from ntds_webportal.organizer import bp as organizer_bp
    app.register_blueprint(organizer_bp, url_prefix='/organizer')

    from ntds_webportal.raffle import bp as raffle_bp
    app.register_blueprint(raffle_bp, url_prefix='/raffle')

    from ntds_webportal.blind_date_assistant import bp as blind_date_assistant_bp
    app.register_blueprint(blind_date_assistant_bp, url_prefix='/blind_date_assistant')

    from ntds_webportal.check_in_assistant import bp as check_in_assistant_bp
    app.register_blueprint(check_in_assistant_bp, url_prefix='/check_in_assistant')

    from ntds_webportal.dancer import bp as dancer_bp
    app.register_blueprint(dancer_bp, url_prefix='/dancer')

    from ntds_webportal.volunteering import bp as volunteering_bp
    app.register_blueprint(volunteering_bp, url_prefix='/volunteering')

    from ntds_webportal.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp, url_prefix='/notifications')

    from ntds_webportal.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app


from ntds_webportal import models
