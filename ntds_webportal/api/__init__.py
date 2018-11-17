from flask import Blueprint

bp = Blueprint('api', __name__)

from ntds_webportal.api.contestant import routes
from ntds_webportal.api.team import routes
from ntds_webportal.api.tournament_state import routes
