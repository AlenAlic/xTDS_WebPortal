import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
SECRET_KEY = 'test-key'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False