from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.notifications import bp
from ntds_webportal.models import Notification, User, requires_access_level
from ntds_webportal.notifications.forms import NotificationForm
import ntds_webportal.data as data


@bp.route('/message_list')
@login_required
def message_list():
    show_archived = request.args.get('show_archived', False, type=bool)
    if show_archived:
        notifications_query = Notification.query.filter_by(user=current_user)
    else:
        notifications_query = Notification.query.filter_by(user=current_user, archived=False)
    notifications = notifications_query.order_by(Notification.notification_id.desc()) \
        .order_by(Notification.unread.desc()).all()
    return render_template('notifications/message_list.html', title="Notifications", notifications=notifications,
                           show_archived=show_archived)


@bp.route('/read/<notification>', methods=['GET'])
@login_required
def read(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.unread = False
        db.session.commit()
        return redirect(url_for('notifications.message_list'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.message_list'))


@bp.route('/unread/<notification>', methods=['GET'])
@login_required
def unread(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.unread = True
        db.session.commit()
        return redirect(url_for('notifications.message_list'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.message_list'))


@bp.route('/archive/<notification>', methods=['GET'])
@login_required
def archive(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.archived = True
        n.unread = False
        db.session.commit()
        return redirect(url_for('notifications.message_list'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.message_list'))


@bp.route('/unarchive/<notification>', methods=['GET'])
@login_required
def unarchive(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.archived = False
        db.session.commit()
        return redirect(url_for('notifications.message_list'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.message_list'))


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
        return redirect(url_for('notifications.message_list'))


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@requires_access_level([data.ACCESS['admin'], data.ACCESS['organizer']])
def create():
    print("Processing Form")
    form = NotificationForm()
    choices = [('tc', 'All Teamcaptains'), ('tr', 'All Treasurers')]
    for user in User.query.all():
        choices.append(('{}'.format(user.user_id), user.username))
    form.recipients.choices = choices
    if form.validate_on_submit():
        for recipient in form.recipients.data:
            if recipient.isdigit():
                u = User.query.filter_by(user_id=recipient).first()
                n = Notification(title=form.title.data, text=form.body.data,
                                 user=u, sender=current_user)
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
    return render_template('notifications/create.html', title="Send message", form=form)
