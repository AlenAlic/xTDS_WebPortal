from flask import render_template
from ntds_webportal import db
from ntds_webportal.errors import bp
from ntds_webportal.errors.email import send_error_email
import traceback


# noinspection PyUnusedLocal
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html')


# noinspection PyUnusedLocal
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html')


# noinspection PyUnusedLocal
# @bp.app_errorhandler(Exception)
# def handle_unexpected_error(error):
#     db.session.rollback()
#     message = traceback.format_exc()
#     message = message.split('\n')
#     status_code = 500
#     send_error_email(status_code, message)
#     return render_template('errors/500.html')
