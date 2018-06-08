from flask import render_template, current_app
from ntds_webportal.email import send_email
from ntds_webportal.tournament_config import tournament_settings


def send_raffle_completed_email(teamcaptain_email):
    send_email(f"{tournament_settings['tournament']} raffle completed",
               sender=current_app.config['ADMINS'][0],
               recipients=[teamcaptain_email],
               text_body=render_template('email/raffle_completed.txt'),
               html_body=render_template('email/raffle_completed.html'))
