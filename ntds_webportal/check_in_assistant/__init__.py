from flask import Blueprint

bp = Blueprint('check_in_assistant', __name__)

from ntds_webportal.check_in_assistant import routes
