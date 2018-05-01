from flask import Blueprint

bp = Blueprint('notifications', __name__)

from ntds_webportal.notifications import routes
