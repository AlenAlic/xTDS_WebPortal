from flask import render_template, current_app
from ntds_webportal.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('xTDS WebPortal Password Reset',
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))


def send_treasurer_activation_email(email, username, password, message):
    send_email('xTDS WebPortal account activation',
               recipients=[email],
               text_body=render_template('email/activate_treasurer.txt',
                                         username=username, password=password, message=message),
               html_body=render_template('email/activate_treasurer.html',
                                         username=username, password=password, message=message),
               bcc=[current_app.config['ADMINS'][0]])


def send_organizer_activation_email(email, username, password, tournament, year, city):
    send_email('xTDS WebPortal account activation', recipients=[email],
               text_body=render_template('email/reset_organizer.txt', username=username, password=password,
                                         tournament=tournament, year=year, city=city),
               html_body=render_template('email/reset_organizer.html', username=username, password=password,
                                         tournament=tournament, year=year, city=city),
               bcc=[current_app.config['ADMINS'][0]])


def send_team_captain_activation_email(email, user, password, tournament, year, city):
    send_email('xTDS WebPortal account activation', recipients=[email],
               text_body=render_template('email/activate_team_captain.txt', username=user.username, password=password,
                                         user=user, tournament=tournament, year=year, city=city),
               html_body=render_template('email/activate_team_captain.html', username=user.username, password=password,
                                         user=user, tournament=tournament, year=year, city=city),
               bcc=[current_app.config['ADMINS'][0]])
