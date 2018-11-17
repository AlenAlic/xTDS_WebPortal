from flask import Blueprint

bp = Blueprint('raffle', __name__)

from ntds_webportal.raffle import routes
