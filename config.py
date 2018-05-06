import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
SECRET_KEY = 'test-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db?check_same_thread=False')
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# mail-server: python -m smtpd -n -c DebuggingServer localhost:8025
# pip freeze > requirements.txt
MAIL_SERVER = 'localhost'
MAIL_PORT = 8025
MAIL_USE_TLS = ''
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
ADMINS = ['your-email@example.com']
