from flask import Blueprint

bp = Blueprint('organizer', __name__)

from ntds_webportal.organizer import routes
