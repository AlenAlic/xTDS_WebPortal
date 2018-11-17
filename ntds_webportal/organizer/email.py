from flask import render_template, g, current_app
from ntds_webportal.email import send_email


def send_raffle_completed_email(teamcaptain_email):
    send_email(f"{g.sc.tournament} raffle completed",
               recipients=[teamcaptain_email],
               text_body=render_template('email/raffle_completed.txt'),
               html_body=render_template('email/raffle_completed.html'))


def send_registration_open_email(email):
    send_email(f"{g.sc.year} {g.sc.tournament} in {g.sc.city} - Registration open", recipients=[email],
               text_body=render_template('email/registration_open.txt',
                                         tournament=g.sc.tournament, year=g.sc.year, city=g.sc.city),
               html_body=render_template('email/registration_open.html',
                                         tournament=g.sc.tournament, year=g.sc.year, city=g.sc.city),
               bcc=[current_app.config['ADMINS'][0]])


def send_super_volunteer_user_account_email(super_volunteer, full_name, super_volunteer_password):
    send_email(f"Registered for {g.sc.year} {g.sc.tournament} in {g.sc.city}",
               recipients=[super_volunteer.email],
               text_body=render_template('email/activate_super_volunteer_user_account.txt',
                                         super_volunteer=super_volunteer, name=full_name,
                                         password=super_volunteer_password),
               html_body=render_template('email/activate_super_volunteer_user_account.html',
                                         super_volunteer=super_volunteer, name=full_name,
                                         password=super_volunteer_password))


def send_gdpr_reminder_email(dancer):
    send_email(f"{g.sc.year} {g.sc.tournament} in {g.sc.city} - GDPR reminder", recipients=[dancer.email],
               text_body=render_template('email/dancer_gdpr_reminder.txt',
                                         tournament=g.sc.tournament, year=g.sc.year, city=g.sc.city, dancer=dancer),
               html_body=render_template('email/dancer_gdpr_reminder.html',
                                         tournament=g.sc.tournament, year=g.sc.year, city=g.sc.city, dancer=dancer))
