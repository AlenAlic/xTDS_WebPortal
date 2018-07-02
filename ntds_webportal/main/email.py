from flask import render_template, current_app
from ntds_webportal.email import send_email


def send_new_messages_email(sender, recipient):
    send_email('New messages - xTDS WebPortal',
               sender=current_app.config['ADMINS'][0],
               recipients=[recipient.email],
               text_body=render_template('email/new_message.txt', sender=sender, recipient=recipient),
               html_body=render_template('email/new_message.html', sender=sender, recipient=recipient))
