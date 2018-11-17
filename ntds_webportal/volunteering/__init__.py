from flask import Blueprint

bp = Blueprint('volunteering', __name__)

from ntds_webportal.volunteering import routes
