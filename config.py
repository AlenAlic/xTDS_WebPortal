import os
import json
# noinspection PyPackageRequirements
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):

    ENV = os.environ.get('ENV') or 'production'
    DEBUG = os.environ.get('DEBUG') == "True" or False

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or ''
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'local@example.com'
    ADMINS = ['local@example.com']

    CACHE_TYPE = "filesystem"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_IGNORE_ERRORS = True
    CACHE_DIR = os.path.join(basedir, "cache")
    CACHE_THRESHOLD = 100

    PRETTY_URL = os.environ.get('PRETTY_URL') or "example.com"
    BASE_URL = "https://" + PRETTY_URL
    ACTIVATE_URL = BASE_URL + "/auth/activate"
    RESET_URL = BASE_URL + "/auth/password/reset"

    allowed_urls = os.environ.get("ALLOWED_URLS")
    ALLOWED_URLS = json.loads(allowed_urls) if allowed_urls else ["http://127.0.0.1:8080", "http://localhost:8080"]


# requirements
# pip freeze > requirements.txt

# MAIL SERVERS
# python -m smtpd -n -c DebuggingServer localhost:8025
# python -u -m smtpd -n -c DebuggingServer localhost:8025 > mail.log

# recompile JSX to Vanilla JS
# npm init -y
# npm install babel-cli@6 babel-preset-react-app@3
# npx babel --watch ntds_webportal/static/react_files --out-dir ntds_webportal/static/src --presets react-app/prod
