from flask import render_template, g
from ntds_webportal.email import send_email


def send_dancer_user_account_email(dancer, full_name, dancer_password):
    send_email(f"Complete your registration for the {g.sc.year} {g.sc.tournament} in {g.sc.city}",
               recipients=[dancer.email],
               text_body=render_template('email/activate_dancer_user_account.txt',
                                         dancer=dancer, name=full_name, password=dancer_password),
               html_body=render_template('email/activate_dancer_user_account.html',
                                         dancer=dancer, name=full_name, password=dancer_password))
