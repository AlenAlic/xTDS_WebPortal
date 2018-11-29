from flask import render_template, request, redirect, url_for, flash, Markup
from flask_login import login_required, current_user
from ntds_webportal import db
from ntds_webportal.volunteering import bp
from ntds_webportal.volunteering.forms import SuperVolunteerForm
from ntds_webportal.models import requires_access_level, requires_tournament_state, User, SuperVolunteer, Contestant, \
    ContestantInfo, StatusInfo
from ntds_webportal.base_functions import random_password
from ntds_webportal.organizer.email import send_super_volunteer_user_account_email
from ntds_webportal.data import *


def create_super_volunteer_user_account(form, super_volunteer):
    super_volunteer_account = User()
    super_volunteer_account.username = form.email.data
    super_volunteer_account.email = form.email.data
    super_volunteer_account_password = random_password()
    super_volunteer_account.set_password(super_volunteer_account_password)
    super_volunteer_account.access = ACCESS[SUPER_VOLUNTEER]
    super_volunteer_account.is_active = True
    super_volunteer_account.send_new_messages_email = True
    super_volunteer_account.super_volunteer = super_volunteer
    db.session.add(super_volunteer_account)
    db.session.commit()
    send_super_volunteer_user_account_email(super_volunteer_account, super_volunteer.get_full_name(),
                                            super_volunteer_account_password)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SuperVolunteerForm()
    if request.method == 'POST':
        form.custom_validate()
    if form.validate_on_submit():
        if 'privacy_checkbox' in request.values:
            super_volunteer = SuperVolunteer()
            super_volunteer.update_data(form)
            db.session.add(super_volunteer)
            db.session.commit()
            flash(Markup(f'<b>Registration complete:</b> {super_volunteer.get_full_name()}, '
                         f'you have been successfully registered as a Super Volunteer.'), 'alert-success')
            create_super_volunteer_user_account(form, super_volunteer)
            return redirect(url_for('main.index'))
        else:
            flash('You can not register without accepting the privacy statement.', 'alert-danger')
    return render_template('volunteering/register_volunteer.html', form=form)


@bp.route('/super_volunteer_data', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[SUPER_VOLUNTEER]])
def super_volunteer_data():
    super_volunteer = current_user.super_volunteer
    form = SuperVolunteerForm()
    if request.method == GET:
        form.populate(super_volunteer)
    if request.method == POST:
        form.custom_validate()
    if form.validate_on_submit():
        super_volunteer.update_data(form)
        db.session.commit()
        flash('Changes saved', 'alert-success')
        return redirect(url_for('main.index'))
    return render_template('volunteering/edit_volunteer.html', form=form)


@bp.route('/volunteers', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_OPEN)
def volunteers():
    # PRIORITY Add same click through link to super volunteers here
    dancers = Contestant.query.join(StatusInfo, ContestantInfo).filter(StatusInfo.status == CONFIRMED)\
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    dancers = [d for d in dancers if d.volunteer_info[0].volunteering()]
    super_volunteers = SuperVolunteer.query.all()
    return render_template('volunteering/volunteers.html', dancers=dancers, super_volunteers=super_volunteers)
