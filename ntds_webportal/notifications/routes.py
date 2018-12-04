from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.notifications import bp
from ntds_webportal.models import Notification, User, requires_access_level
from ntds_webportal.notifications.forms import NotificationForm
from ntds_webportal.data import *
from sqlalchemy import or_


@bp.route('/messages', methods=['GET'])
@login_required
def messages():
    # WISH - Filter messages based on title
    inbox_messages = Notification.query.filter_by(user=current_user, archived=False)\
        .order_by(Notification.notification_id.desc(), Notification.unread.desc()).all()
    archived_messages = Notification.query.filter_by(user=current_user, archived=True) \
        .order_by(Notification.notification_id.desc(), Notification.unread.desc()).all()
    sent_messages = Notification.query.filter_by(sender=current_user) \
        .order_by(Notification.notification_id.desc()).all()
    return render_template('notifications/messages.html', title="Notifications", inbox_messages=inbox_messages,
                           archived_messages=archived_messages, sent_messages=sent_messages)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@requires_access_level(MESSAGES_ACCESS)
def create():
    form = NotificationForm()
    choices = [('tc', 'All Teamcaptains'), ('tr', 'All Treasurers')]
    for user in User.query.filter(User.is_active.is_(True), User.user_id != current_user.user_id,
                                  or_(User.access == ACCESS[ADMIN], User.access == ACCESS[ORGANIZER],
                                      User.access == ACCESS[TEAM_CAPTAIN], User.access == ACCESS[TREASURER],
                                      User.access == ACCESS[TREASURER])).order_by(User.username).all():
        choices.append(('{}'.format(user.user_id), user.username))
    form.recipients.choices = choices
    if request.method == 'GET' and len(request.args) > 0:
        form.recipients.data = [request.args.get('user_id')]
        notification_id = request.args.get('notification_id', default=None, type=int)
        if notification_id is not None:
            n = Notification.query.filter(Notification.notification_id == notification_id).first()
            if n is not None:
                n.unread = False
                db.session.commit()
                form.body.data = "\r\n\r\n\r\n====== Original Message ======\r\n\r\n" + n.text
                form.title.data = 'Re: ' + n.title
    if form.validate_on_submit():
        for recipient in form.recipients.data:
            if recipient.isdigit():
                u = User.query.filter_by(user_id=recipient).first()
                n = Notification(title=form.title.data, text=form.body.data,
                                 user=u, sender=current_user)
                n.send()
                if u.access == ACCESS[TREASURER] and current_user.team != u.team:
                    tc = User.query.filter(User.access == ACCESS[TEAM_CAPTAIN], User.is_active.is_(True),
                                           User.team == u.team).first()
                    n = Notification(title=form.title.data, text='Message sent to your treasurer:\n\n'+form.body.data,
                                     user=tc, sender=current_user)
                    n.send()
            else:
                users = []
                if recipient == 'tc':
                    users = User.query.filter(User.access == ACCESS[TEAM_CAPTAIN], User.is_active.is_(True),
                                              User.user_id != current_user.user_id).all()
                if recipient == 'tr':
                    users = User.query.filter(User.access == ACCESS[TREASURER], User.is_active.is_(True),
                                              User.user_id != current_user.user_id).all()
                for u in users:
                    n = Notification(title=form.title.data, text=form.body.data,
                                     user=u, sender=current_user)
                    n.send()
        flash('Message(s) submitted')
        return redirect(url_for('notifications.messages'))
    return render_template('notifications/create.html', title="Send message", form=form)


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
