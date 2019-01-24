from flask import Blueprint

bp = Blueprint('as_api', __name__)

from ntds_webportal.adjudication_system.api import adjudication
from ntds_webportal.adjudication_system.api import tournament_office
from ntds_webportal.adjudication_system.api import floor_manager
