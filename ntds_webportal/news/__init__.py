from flask import Blueprint

bp = Blueprint('news_items', __name__)

from ntds_webportal.news import routes
