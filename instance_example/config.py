from ntds_webportal.values import PRODUCTION_ENV

ENV = PRODUCTION_ENV
SECRET_KEY = 'secret_key'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost:3306/databasename'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = False

MAIL_SERVER = 'localhost'
MAIL_PORT = 8025
MAIL_USE_TLS = ''
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
ADMINS = ['email@example.com']

# Debut toolbar
DEBUG_TB_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False
