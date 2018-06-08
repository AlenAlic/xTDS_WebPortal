from flask import render_template, url_for, redirect, flash
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.notifications import bp
from ntds_webportal.models import Notification, User, requires_access_level
from ntds_webportal.notifications.forms import NotificationForm
import ntds_webportal.data as data
from ntds_webportal.data import *


@bp.route('/messages')
@login_required
def messages():
    inbox_messages = Notification.query.filter_by(user=current_user, archived=False)\
        .order_by(Notification.notification_id.desc(), Notification.unread.desc()).all()
    archived_messages = Notification.query.filter_by(user=current_user, archived=True) \
        .order_by(Notification.notification_id.desc(), Notification.unread.desc()).all()
    sent_messages = Notification.query.filter_by(sender=current_user) \
        .order_by(Notification.notification_id.desc()).all()
    return render_template('notifications/messages.html', title="Notifications", inbox_messages=inbox_messages,
                           archived_messages=archived_messages, sent_messages=sent_messages)


@bp.route('/read/<notification>', methods=['GET'])
@login_required
def read(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.unread = False
        db.session.commit()
        return redirect(url_for('notifications.messages'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.messages'))


@bp.route('/unread/<notification>', methods=['GET'])
@login_required
def unread(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.unread = True
        db.session.commit()
        return redirect(url_for('notifications.messages'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.messages'))


@bp.route('/archive/<notification>', methods=['GET'])
@login_required
def archive(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.archived = True
        n.unread = False
        db.session.commit()
        return redirect(url_for('notifications.messages'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.messages'))


@bp.route('/unarchive/<notification>', methods=['GET'])
@login_required
def unarchive(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.archived = False
        db.session.commit()
        return redirect(url_for('notifications.messages'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.messages'))


@bp.route('/goto/<notification>', methods=['GET'])
@login_required
def goto(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.unread = False
        db.session.commit()
        return redirect(n.destination)
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.messages'))


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS['admin'], ACCESS['organizer'], ACCESS['team_captain'], ACCESS['treasurer']])
def create():
    form = NotificationForm()
    choices = [('tc', 'All Teamcaptains'), ('tr', 'All Treasurers')]
    for user in User.query.filter(User.is_active.is_(True)).all():
        choices.append(('{}'.format(user.user_id), user.username))
    form.recipients.choices = choices
    if form.validate_on_submit():
        for recipient in form.recipients.data:
            if recipient.isdigit():
                u = User.query.filter_by(user_id=recipient).first()
                n = Notification(title=form.title.data, text=form.body.data,
                                 user=u, sender=current_user)
                db.session.add(n)
                if u.access == ACCESS['treasurer'] and current_user.team != u.team:
                    tc = User.query.filter(User.access == ACCESS['team_captain'], User.team == u.team).first()
                    n = Notification(title=form.title.data, text='Message sent to your treasurer:\n\n'+form.body.data,
                                     user=tc, sender=current_user)
                    db.session.add(n)
            else:
                users = []
                if recipient == 'tc':
                    users = User.query.filter_by(access=data.ACCESS['team_captain']).all()
                if recipient == 'tr':
                    users = User.query.filter_by(access=data.ACCESS['treasurer']).all()
                for u in users:
                    n = Notification(title=form.title.data, text=form.body.data,
                                     user=u, sender=current_user)
                    db.session.add(n)
        db.session.commit()
        flash('Message(s) submitted')
        return redirect(url_for('notifications.messages'))
    return render_template('notifications/create.html', title="Send message", form=form)
