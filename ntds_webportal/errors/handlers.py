from flask import render_template, request, current_app
from ntds_webportal import db
from ntds_webportal.errors import bp
from ntds_webportal.errors.email import send_error_email
import traceback
from ntds_webportal.api.errors import error_response as api_error_response


def wants_json_response():
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']


# noinspection PyUnusedLocal
@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html')


# noinspection PyUnusedLocal
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html')


# noinspection PyUnusedLocal
@bp.app_errorhandler(Exception)
def handle_unexpected_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    message = traceback.format_exc()
    message = message.split('\n')
    status_code = 500
    send_error_email(status_code, message)
    return render_template('errors/500.html', message=message if current_app.config.get('DEBUG') else None)
