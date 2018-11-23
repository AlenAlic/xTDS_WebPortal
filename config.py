import os

basedir = os.path.abspath(os.path.dirname(__file__))

ENV = 'development'
SECRET_KEY = 'test-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db?check_same_thread=False')
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = False

# MAIL SERVERS
# python -m smtpd -n -c DebuggingServer localhost:8025
# python -u -m smtpd -n -c DebuggingServer localhost:8025 > mail.log
MAIL_SERVER = 'localhost'
MAIL_PORT = 8025
MAIL_USE_TLS = ''
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
ADMINS = ['your-email@example.com']

DEBUG_TB_INTERCEPT_REDIRECTS = False

# requirements
# pip freeze > requirements.txt
# recompile JSX to Vanilla JS
# npx babel --watch dev_react --out-dir src --presets react-app/prod
