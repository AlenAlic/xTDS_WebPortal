from flask import Blueprint

bp = Blueprint('blind_date_assistant', __name__)

from ntds_webportal.blind_date_assistant import routes
