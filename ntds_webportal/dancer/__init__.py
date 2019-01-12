from flask import Blueprint

bp = Blueprint('url_dancer', __name__)

from ntds_webportal.dancer import routes
