from flask import Blueprint

bp = Blueprint('self_admin', __name__)

from ntds_webportal.self_admin import routes
