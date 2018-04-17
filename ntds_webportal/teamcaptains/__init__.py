from flask import Blueprint

bp = Blueprint('teamcaptains', __name__)

from ntds_webportal.teamcaptains import routes
