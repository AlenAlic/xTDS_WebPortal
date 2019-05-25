from flask import Flask, redirect, url_for, g, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, logout_user, AnonymousUserMixin
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_debugtoolbar import DebugToolbarExtension
from wtforms import PasswordField
import ntds_webportal.data as data
from datetime import datetime
from ntds_webportal.util import BooleanConverter, random_password


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_admin() or current_user.is_tournament_office_manager():
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
    page_size = 1000

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index'))


class AdjudicatorSystemView(BaseView):
    def is_accessible(self):
        return current_user.is_admin() or current_user.is_tournament_office_manager()


class UserView(BaseView):
    column_exclude_list = ['password_hash', ]
    form_excluded_columns = ['password_hash', ]
    form_extra_fields = {'password2': PasswordField('Password')}

    # noinspection PyPep8Naming
    def on_model_change(self, form, User, is_created):
        if form.password2.data != '':
            User.set_password(form.password2.data)


class Anonymous(AnonymousUserMixin):

    @staticmethod
    def is_admin():
        return False

    @staticmethod
    def is_organizer():
        return False

    @staticmethod
    def is_tc():
        return False

    @staticmethod
    def is_treasurer():
        return False

    @staticmethod
    def is_bda():
        return False

    @staticmethod
    def is_cia():
        return False

    @staticmethod
    def is_ada():
        return False

    @staticmethod
    def is_dancer():
        return False

    @staticmethod
    def is_super_volunteer():
        return False

    @staticmethod
    def is_tournament_office_manager():
        return False

    @staticmethod
    def is_floor_manager():
        return False

    @staticmethod
    def is_adjudicator():
        return False


def create_app():
    """
    Create instance of website.
    """
    from ntds_webportal.models import User, Team, Contestant, ContestantInfo, DancingInfo, StatusInfo, PaymentInfo, \
        VolunteerInfo, AdditionalInfo, MerchandiseInfo, Notification, PartnerRequest, NameChangeRequest, \
        TournamentState, SystemConfiguration, RaffleConfiguration, AttendedPreviousTournamentContestant, \
        NotSelectedContestant, SuperVolunteer, ShiftInfo, Shift, ShiftSlot, MerchandiseItem, MerchandiseItemVariant, \
        MerchandisePurchase
    from ntds_webportal.models import Event, Competition, DancingClass, Discipline, Dance, Round, \
        Heat, Couple, Adjudicator, Mark, CouplePresent, RoundResult, FinalPlacing, DanceActive, CompetitionMode, Dancer

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')
    app.url_map.strict_slashes = False

    app.url_map.converters['bool'] = BooleanConverter

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:'))
    login.init_app(app)
    login.login_view = 'main.index'
    login.anonymous_user = Anonymous
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
    admin.add_view(BaseView(MerchandiseItem, db.session))
    admin.add_view(BaseView(MerchandiseItemVariant, db.session))
    admin.add_view(BaseView(MerchandisePurchase, db.session))
    admin.add_view(BaseView(Notification, db.session))
    admin.add_view(BaseView(PartnerRequest, db.session))
    admin.add_view(BaseView(NameChangeRequest, db.session))
    admin.add_view(BaseView(TournamentState, db.session))
    admin.add_view(BaseView(SystemConfiguration, db.session))
    admin.add_view(BaseView(RaffleConfiguration, db.session))
    admin.add_view(BaseView(AttendedPreviousTournamentContestant, db.session))
    admin.add_view(BaseView(NotSelectedContestant, db.session))
    admin.add_view(BaseView(SuperVolunteer, db.session))
    admin.add_view(BaseView(ShiftInfo, db.session))
    admin.add_view(BaseView(Shift, db.session))
    admin.add_view(BaseView(ShiftSlot, db.session))
    admin.add_view(AdjudicatorSystemView(Event, db.session))
    admin.add_view(AdjudicatorSystemView(Competition, db.session))
    admin.add_view(AdjudicatorSystemView(DancingClass, db.session))
    admin.add_view(AdjudicatorSystemView(Discipline, db.session))
    admin.add_view(AdjudicatorSystemView(Dance, db.session))
    admin.add_view(AdjudicatorSystemView(Adjudicator, db.session))
    admin.add_view(AdjudicatorSystemView(Dancer, db.session))
    admin.add_view(AdjudicatorSystemView(Couple, db.session))
    admin.add_view(AdjudicatorSystemView(Round, db.session))
    admin.add_view(AdjudicatorSystemView(DanceActive, db.session))
    admin.add_view(AdjudicatorSystemView(Heat, db.session))
    admin.add_view(AdjudicatorSystemView(Mark, db.session))
    admin.add_view(AdjudicatorSystemView(FinalPlacing, db.session))
    admin.add_view(AdjudicatorSystemView(CouplePresent, db.session))
    admin.add_view(AdjudicatorSystemView(RoundResult, db.session))
    toolbar.init_app(app)

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
        g.unpublished_shifts = len(Shift.query.filter(Shift.published.is_(False), Shift.info_id.isnot(None)).all())
        g.event = Event.query.first()
        g.competitions = Competition.query.all()
        g.competition_mode = CompetitionMode

    @app.context_processor
    def inject_now():
        return {'now': f"?{int(datetime.utcnow().timestamp())}"}

    @app.shell_context_processor
    def make_shell_context():
        return {'create_admin': create_admin, 'create_configuration': create_configuration}

    def create_admin(email, password):
        if len(User.query.filter(User.access == data.ACCESS[data.ADMIN]).all()) == 0:
            a = User()
            a.username = 'admin'
            a.email = email
            a.set_password(password)
            a.access = data.ACCESS[data.ADMIN]
            a.is_active = True
            db.session.add(admin)
            db.session.commit()

    def create_configuration():
        if User.query.filter(User.access == data.ACCESS[data.ORGANIZER]).first() is None:
            organisation = User()
            organisation.username = 'NTDSEnschede2018'
            organisation.email = 'email@example.com'
            organisation.set_password(random_password())
            organisation.access = data.ACCESS[data.ORGANIZER]
            organisation.is_active = False
            db.session.add(organisation)
            db.session.commit()
        for a in data.ASSISTANTS:
            if User.query.filter(User.username == a).first() is None:
                assistant = User()
                assistant.username = a
                assistant.set_password(random_password())
                assistant.access = data.ACCESS[data.ASSISTANTS[a]]
                assistant.is_active = False
                db.session.add(assistant)
        db.session.commit()
        if Team.query.filter(Team.name == data.TEAM_ORGANIZATION).first() is not None:
            db.session.add(Team(name=data.TEAM_ORGANIZATION, country=data.TEAM_ORGANIZATION,
                                city=data.TEAM_ORGANIZATION))
            db.session.commit()
        if Team.query.filter(Team.name == data.TEAM_SUPER_VOLUNTEER).first() is not None:
            db.session.add(Team(name=data.TEAM_SUPER_VOLUNTEER, country=data.TEAM_SUPER_VOLUNTEER,
                                city=data.TEAM_SUPER_VOLUNTEER))
            db.session.commit()
        if Team.query.filter(Team.name == data.TEAM_ADJUDICATOR).first() is not None:
            db.session.add(Team(name=data.TEAM_ADJUDICATOR, country=data.TEAM_ADJUDICATOR,
                                city=data.TEAM_ADJUDICATOR))
            db.session.commit()
        if len(TournamentState.query.all()) == 0:
            db.session.add(TournamentState())
        if len(SystemConfiguration.query.all()) == 0:
            db.session.add(SystemConfiguration(website_accessible=True))
        if len(RaffleConfiguration.query.all()) == 0:
            db.session.add(RaffleConfiguration())

    with app.app_context():
        from sqlalchemy.exc import InternalError, ProgrammingError
        try:
            if len(TournamentState.query.all()) == 0:
                db.session.add(TournamentState())
            if len(SystemConfiguration.query.all()) == 0:
                db.session.add(SystemConfiguration())
            if len(RaffleConfiguration.query.all()) == 0:
                db.session.add(RaffleConfiguration())
            db.session.commit()
        except (InternalError, ProgrammingError):
            pass

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

    from ntds_webportal.adjudication_system import bp as adjudication_system_bp
    app.register_blueprint(adjudication_system_bp, url_prefix='/adjudication_system')

    from ntds_webportal.adjudication_system.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/adjudication_system/api')

    # from ntds_webportal.companion_app import bp as app_bp
    # app.register_blueprint(app_bp, url_prefix='/app')

    return app


# noinspection PyPep8
from ntds_webportal import models
