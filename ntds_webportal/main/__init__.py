from flask import Blueprint

bp = Blueprint('main', __name__)

from ntds_webportal.main import routes
