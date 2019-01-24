from flask import Blueprint

bp = Blueprint('adjudication_system', __name__)

from ntds_webportal.adjudication_system import routes
