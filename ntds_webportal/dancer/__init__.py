from flask import Blueprint

bp = Blueprint('dancer', __name__)

from ntds_webportal.dancer import routes
