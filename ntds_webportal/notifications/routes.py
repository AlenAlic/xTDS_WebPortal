from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_required
from ntds_webportal import db
from ntds_webportal.notifications import bp
from ntds_webportal.models import Notification


@bp.route('/list')
@login_required
def list():
    show_archived = request.args.get('show_archived', False, type=bool)
    if show_archived:
        notifications = Notification.query.filter_by(user=current_user) \
            .order_by(Notification.unread.desc()).all()
    else:
        notifications = Notification.query.filter_by(user=current_user, archived=False) \
            .order_by(Notification.unread.desc()).all()
    return render_template('notifications/list.html', title="Notifications", notifications=notifications, show_archived=show_archived)


@bp.route('/read/<notification>', methods=['GET'])
@login_required
def read(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.unread = False
        db.session.commit()
        return redirect(url_for('notifications.list'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.list'))


@bp.route('/unread/<notification>', methods=['GET'])
@login_required
def unread(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.unread = True
        db.session.commit()
        return redirect(url_for('notifications.list'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.list'))


@bp.route('/archive/<notification>', methods=['GET'])
@login_required
def archive(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.archived = True
        n.unread = False
        db.session.commit()
        return redirect(url_for('notifications.list'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.list'))


@bp.route('/unarchive/<notification>', methods=['GET'])
@login_required
def unarchive(notification):
    n = Notification.query.filter_by(notification_id=notification).first()
    if n:
        n.archived = False
        db.session.commit()
        return redirect(url_for('notifications.list'))
    else:
        flash('Notification not found or inaccessible!'.format(notification))
        return redirect(url_for('notifications.list'))
