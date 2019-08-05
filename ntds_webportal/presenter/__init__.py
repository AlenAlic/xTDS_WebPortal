from flask import Blueprint

bp = Blueprint('presenter', __name__)

from ntds_webportal.presenter import routes
