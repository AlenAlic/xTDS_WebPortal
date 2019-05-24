from flask import Blueprint

bp = Blueprint('api', __name__)

from ntds_webportal.api import errors
from ntds_webportal.api import contestants
from ntds_webportal.api import teams
from ntds_webportal.api import tournament_state
from ntds_webportal.api import users
