from flask import Blueprint

bp = Blueprint('auth', __name__)

from ntds_webportal.auth import routes
