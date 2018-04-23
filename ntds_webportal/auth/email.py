from flask import render_template, current_app
from ntds_webportal.email import send_email
import random
import string


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('xTDS WebPortal Password Reset',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))


def send_treasurer_activation_email(email, username, password, message):
    send_email('xTDS WebPortal account activation',
               sender=current_app.config['ADMINS'][0],
               recipients=[email],
               text_body=render_template('email/activate_treasurer.txt',
                                         username=username, password=password, message=message),
               html_body=render_template('email/activate_treasurer.html',
                                         username=username, password=password, message=message))


def random_password():
    allowed_chars = string.ascii_letters + '0123456789'
    return ''.join(random.sample(allowed_chars, 12))
