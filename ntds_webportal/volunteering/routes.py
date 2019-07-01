from flask import render_template, request, redirect, url_for, flash, g
from flask_login import login_required, current_user
from ntds_webportal import db
from ntds_webportal.volunteering import bp
from ntds_webportal.volunteering.forms import SuperVolunteerForm, ShiftTypeForm, ShiftForm, ShiftSlotForm
from ntds_webportal.models import requires_access_level, requires_tournament_state, User, SuperVolunteer, Contestant, \
    ContestantInfo, StatusInfo, Shift, ShiftInfo, ShiftSlot, Team
from ntds_webportal.util import random_password
from ntds_webportal.organizer.email import send_super_volunteer_user_account_email
from ntds_webportal.data import *
from sqlalchemy import or_, and_
from datetime import timedelta, datetime
from ntds_webportal.functions import str2bool, hours_delta


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
    if current_user.is_organizer():
        super_volunteer_account.team = Team.query.filter(Team.name == TEAM_ORGANIZATION).first()
    else:
        super_volunteer_account.team = Team.query.filter(Team.name == TEAM_SUPER_VOLUNTEER).first()
    db.session.add(super_volunteer_account)
    db.session.commit()
    send_super_volunteer_user_account_email(super_volunteer_account, super_volunteer.get_full_name(),
                                            super_volunteer_account_password)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SuperVolunteerForm()
    if g.ts.super_volunteer_registration_open or current_user.is_organizer():
        if request.method == 'POST':
            form.custom_validate()
            all_users = User.query.all()
            emails = [u.email for u in all_users if u.email is not None]
            form_email = form.email.data
            if form_email in emails and form_email is not None:
                flash(f'There is already a dancer registered with the e-mail address {form.email.data}.<br/>'
                      f'You cannot register as both a dancer in the tournament, and a Super Volunteer.<br/>'
                      f'If you are already registered as a dancer, and wish to be a Super Volunteer instead, '
                      f'please contact your teamcaptain to completely remove your registration as a dancer '
                      f'from the tournament first. Afterwards, you can register as a Super Volunteer.',
                      "alert-danger")
            else:
                if form.validate_on_submit():
                    if 'privacy_checkbox' in request.values:
                        super_volunteer = SuperVolunteer()
                        super_volunteer.update_data(form)
                        db.session.add(super_volunteer)
                        db.session.commit()
                        flash(f'<b>Registration complete:</b> {super_volunteer.get_full_name()}, '
                              f'you have been successfully registered as a Super Volunteer.', 'alert-success')
                        # noinspection PyTypeChecker
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
    dancers = Contestant.query.join(StatusInfo, ContestantInfo).filter(StatusInfo.status == CONFIRMED)\
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    dancers = [d for d in dancers if d.volunteer_info.wants_to_volunteer()]
    super_volunteers = SuperVolunteer.query.all()
    return render_template('volunteering/volunteers.html', dancers=dancers, super_volunteers=super_volunteers)


@bp.route('/super_volunteers_management', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(TEAM_CAPTAINS_HAVE_ACCESS)
def super_volunteers_management():
    form = request.args
    if 'close_registration' in form:
        g.ts.super_volunteer_registration_open = False
        flash(f"Super Volunteer registration for the {g.sc.tournament} has been closed.", "alert-info")
    if 'open_registration' in form:
        g.ts.super_volunteer_registration_open = True
        flash(f"Super Volunteer registration for the {g.sc.tournament} has been opened.", "alert-info")
    if len(form) > 0:
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('volunteering/super_volunteers_management.html')


@bp.route('/volunteering_management', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def volunteering_management():
    form = request.args
    if 'open_volunteering_system' in form:
        g.ts.volunteering_system_open = True
        users = User.query.filter(User.access == ACCESS[SUPER_VOLUNTEER], User.team.is_(None)).all()
        super_volunteer_team = Team.query.filter(Team.name == TEAM_SUPER_VOLUNTEER).first()
        for user in users:
            user.team = super_volunteer_team
        flash(f"Team captains, Super Volunteers and dancers now have access to the Volunteering System tab!",
              "alert-success")
        db.session.commit()
        return redirect(url_for('volunteering.shifts'))
    return render_template('volunteering/volunteering_management.html')


@bp.route('/tasks', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def tasks():
    task_list = ShiftInfo.query.order_by(ShiftInfo.name).all()
    return render_template('volunteering/tasks.html', task_list=task_list)


@bp.route('/task/create', methods=['POST', 'GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def create_task():
    form = ShiftTypeForm()
    if form.validate_on_submit():
        db.session.add(ShiftInfo(name=form.name.data, location=form.location.data,
                                 coordinator=form.coordinator.data, description=form.description.data))
        db.session.commit()
        flash(f"Added shift type: {form.name.data}")
        return redirect(url_for('volunteering.tasks'))
    return render_template('volunteering/create_task.html', form=form)


@bp.route('/task/edit/<shift_id>', methods=['POST', 'GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def edit_task(shift_id):
    form = ShiftTypeForm()
    task = ShiftInfo.query.get(shift_id)
    form.submit.label.text = "Save changes"
    if form.validate_on_submit():
        task.name = form.name.data
        task.location = form.location.data
        task.coordinator = form.coordinator.data
        task.description = form.description.data
        db.session.add(task)
        db.session.commit()
        flash(f"Updated shift type: {form.name.data}")
        return redirect(url_for('volunteering.tasks'))
    form.populate(task)
    return render_template('volunteering/edit_task.html', form=form, task=task)


@bp.route('/task/delete/<int:shift_info_id>', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def delete_task(shift_info_id):
    task = ShiftInfo.query.get(shift_info_id)
    if task is not None:
        flash(f"{task.name} deleted.")
        db.session.delete(task)
        db.session.commit()
    else:
        flash("Task not found.")
    return redirect(url_for('volunteering.tasks'))


@bp.route('/shifts', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[TEAM_CAPTAIN]])
def shifts():
    if current_user.is_tc() and not g.ts.volunteering_system_open:
        flash("This page is not accessible yet.")
        return redirect(url_for('main.dashboard'))
    all_tasks = ShiftInfo.query.order_by(ShiftInfo.name).all()
    if current_user.is_organizer():
        shift_list = Shift.query.order_by(Shift.start_time).all()
    else:
        shift_list = Shift.query.join(ShiftSlot)\
            .filter(or_(ShiftSlot.team == current_user.team,
                        and_(ShiftSlot.team_id.is_(None), ShiftSlot.mandatory.is_(False)),
                        and_(ShiftSlot.user_id.isnot(None), ShiftSlot.mandatory.is_(True))),
                    Shift.published.is_(True))\
            .order_by(Shift.start_time).all()
        shift_list = [s for s in shift_list if s.has_slots_available(current_user.team)]
    task_list = {task: [shift for shift in shift_list if shift.info == task] for task in all_tasks}
    if current_user.is_organizer():
        filled_list = {task: sum([shift.filled_slots() for shift in shift_list if shift.info == task])
                       for task in all_tasks}
        slots_list = {task: sum([len(shift.slots) for shift in shift_list if shift.info == task])
                      for task in all_tasks}
        return render_template('volunteering/shifts.html', shifts=shift_list, task_list=task_list,
                               filled_list=filled_list, slots_list=slots_list)
    else:
        task_list = {task: task_list[task] for task in task_list if len(task_list[task]) > 0}
        all_volunteers = Contestant.query.join(ContestantInfo, StatusInfo)\
            .filter(ContestantInfo.team == current_user.team, StatusInfo.status == CONFIRMED)\
            .order_by(Contestant.first_name).all()
        days = sorted(set([s.start_time.date() for s in shift_list]))
        sorted_shifts = {day: [s for s in shift_list if s.start_time.date() == day] for day in days}
        team_slots = ShiftSlot.query.filter(ShiftSlot.team == current_user.team).all()
        team_slots = [s for s in team_slots if s.shift.published]
        organization_slots = ShiftSlot.query.filter(ShiftSlot.mandatory.is_(True), ShiftSlot.user_id.isnot(None),
                                                    ShiftSlot.team_id.is_(None)).all()
        organization_slots = [s for s in organization_slots if s.user.team == current_user.team and s.shift.published]
        hours = {'total': hours_delta(sum([s.duration() for s in team_slots], timedelta(0, 0))),
                 'filled': hours_delta(sum([s.duration() for s in team_slots if s.user is not None], timedelta(0, 0))),
                 'freelance': hours_delta(sum([s.duration() for s in organization_slots], timedelta(0, 0)))
                 }
        return render_template('volunteering/shifts.html', shifts=shift_list, task_list=task_list,
                               all_volunteers=all_volunteers, sorted_shifts=sorted_shifts, hours=hours)


@bp.route('/shift/<int:shift_id>', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[TEAM_CAPTAIN]])
def single_shift(shift_id):
    shift = Shift.query.get(shift_id)
    if shift is None:
        flash("Shift not found.")
        return redirect(url_for('volunteering.shifts'))
    return render_template('volunteering/shift.html', shift=shift)


@bp.route('/shift/create', methods=['POST', 'GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def create_shift():
    form = ShiftForm()
    form.stop_time.validators = []
    if form.validate_on_submit():
        dummy_shift, start_time, stop_time = None, None, None
        for j in range(form.repeats.data):
            shift = Shift()
            shift.info = ShiftInfo.query.get(form.type.data)
            shift.start_time = form.start_time.data + timedelta(hours=form.duration.data.hour*j,
                                                                minutes=form.duration.data.minute)
            shift.stop_time = shift.start_time + timedelta(hours=form.duration.data.hour,
                                                           minutes=form.duration.data.minute)
            for i in range(form.slots.data):
                slot = ShiftSlot()
                slot.mandatory = str2bool(form.mandatory.data)
                if form.team.data > 0:
                    slot.team = Team.query.get(form.team.data)
                shift.slots.append(slot)
            db.session.add(shift)
            if j == 0:
                start_time = shift.start_time
            stop_time = shift.stop_time
            dummy_shift = shift
            if form.repeats.data == 1:
                flash(f"Added shift {shift}")
        if form.repeats.data > 1:
            flash(f"Added {form.repeats.data} shifts of {form.duration.data.strftime('%H:%M')} hour:"
                  f" {dummy_shift.info}, from {start_time.strftime('%H:%M')} to {stop_time.strftime('%H:%M')}.")
        db.session.commit()
        return redirect(url_for('volunteering.shifts', task_id=dummy_shift.info.shift_info_id))
    return render_template('volunteering/create_shift.html', form=form)


@bp.route('/shift/edit/<shift_id>', methods=['POST', 'GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def edit_shift(shift_id):
    form = ShiftForm()
    form.submit.label.text = "Save changes"
    form.slots.description = 'Increasing the number of slots in this shift will create new slots, with the Team and ' \
                             'Mandatory settings from below. Decreasing the amount of shifts will remove excess ' \
                             'shifts, starting from the bottom.'
    shift = Shift.query.get(shift_id)
    if request.method == 'POST':
        if form.validate_on_submit():
            shift.info = ShiftInfo.query.get(form.type.data)
            shift.start_time = form.start_time.data
            shift.stop_time = form.stop_time.data
            if form.slots.data < len(shift.slots):
                slots_to_delete = shift.slots[form.slots.data-len(shift.slots):]
                for slot in slots_to_delete:
                    db.session.delete(slot)
            elif form.slots.data > len(shift.slots):
                for i in range(form.slots.data - len(shift.slots)):
                    slot = ShiftSlot()
                    slot.mandatory = str2bool(form.mandatory.data)
                    if form.team.data > 0:
                        slot.team = Team.query.get(form.team.data)
                    shift.slots.append(slot)
            db.session.commit()
            flash(f"Updated shift {shift}")
            return redirect(url_for('volunteering.single_shift', shift_id=shift_id))
    form.populate(shift)
    return render_template('volunteering/edit_shift.html', form=form, shift=shift)


@bp.route('/shift/delete/<int:shift_id>', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def delete_shift(shift_id):
    shift = Shift.query.get(shift_id)
    task_id = None
    if shift is not None:
        flash(f"{shift} deleted.")
        task_id = shift.info.shift_info_id
        db.session.delete(shift)
        db.session.commit()
    else:
        flash("Shift not found.")
    return redirect(url_for('volunteering.shifts', task_id=task_id))


@bp.route('/slot/<int:slot_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[TEAM_CAPTAIN]])
def shift_slot(slot_id):
    slot = ShiftSlot.query.get(slot_id)
    form = ShiftSlotForm()
    task_id = request.args.get("task_id", default=None)
    if current_user.is_tc():
        if not slot.is_editable(current_user.team):
            flash("You cannot edit this shift, it is not part of your team!", "alert-warning")
            return redirect(url_for('volunteering.shifts',
                                    task_id=task_id if task_id is not None else slot.shift.info.shift_info_id))
        form.submit.label.text = 'Assign dancer'
        form.volunteer.description = 'Assigning a dancer to this shift wil automatically claim the shift for your team.'
        form.mandatory.validators = []
        form.mandatory.data = str(False)
    if request.method == 'POST':
        if form.submit.name in request.form:
            if form.validate_on_submit():
                volunteer = User.query.get(form.volunteer.data) if form.volunteer.data > 0 else None
                team = Team.query.get(form.team.data) if form.team.data > 0 else None
                if current_user.is_organizer():
                    if not slot.user_assigned_to_shift(volunteer):
                        if volunteer is not None:
                            test_shifts = Shift.query.join(ShiftSlot).filter(ShiftSlot.user == volunteer).all()
                            test_shifts = [s for s in test_shifts if not (slot.shift.stop_time <= s.start_time or
                                                                          slot.shift.start_time >= s.stop_time)]
                            if len(test_shifts) > 0:
                                flash(f"Added {volunteer} to {slot.shift}.<br/>{volunteer} is already assigned "
                                      f"to {test_shifts[0]} at the same time, so make sure that this is is "
                                      f"possible!", "alert-warning")
                        slot.user = volunteer
                        slot.team = team
                        if volunteer is not None and team is not None:
                            if team != volunteer.team:
                                slot.user = None
                                flash(f'Did not add {volunteer} to slot, he/she is not part of team {team}',
                                      'alert-warning')
                        slot.mandatory = str2bool(form.mandatory.data)
                        db.session.commit()
                        flash('Changes saved.')
                        return redirect(url_for('volunteering.single_shift', shift_id=slot.shift.shift_id))
                    else:
                        flash(f'Cannot assign {volunteer}, he/she is already assigned to a slot in this shift.',
                              'alert-warning')
                else:
                    slot.team = current_user.team
                    if volunteer is not None:
                        test_shifts = Shift.query.join(ShiftSlot).filter(ShiftSlot.user == volunteer).all()
                        test_shifts = [s for s in test_shifts if not (slot.shift.stop_time <= s.start_time or
                                                                      slot.shift.start_time >= s.stop_time)]
                        if len(test_shifts) > 0:
                            flash(f"Cannot add {volunteer} to {slot.shift}.<br/>{volunteer} is already assigned "
                                  f"to {test_shifts[0]}.", "alert-danger")
                            return redirect(url_for('volunteering.shift_slot', slot_id=slot.slot_id))
                        if not slot.user_assigned_to_shift(volunteer):
                            slot.user = volunteer
                            db.session.commit()
                            flash(f'Assigned {volunteer} to shift {slot.shift}.')
                            return redirect(url_for('volunteering.shifts',
                                                    task_id=task_id if task_id is not None
                                                    else slot.shift.info.shift_info_id))
                        else:
                            flash(f'Cannot assign {volunteer}, he/she is already assigned to a slot in this shift.',
                                  'alert-warning')
                    else:
                        flash(f'Cleared slot of shift {slot.shift}.')
                        slot.user = None
                        db.session.commit()
                        return redirect(url_for('volunteering.shifts',
                                                task_id=task_id if task_id is not None
                                                else slot.shift.info.shift_info_id))
        if current_user.is_tc():
            if 'claim' in request.form:
                slot.team = current_user.team
                db.session.commit()
                flash(f'Claimed slot in shift {slot.shift}.')
                return redirect(url_for('volunteering.shifts',
                                        task_id=task_id if task_id is not None else slot.shift.info.shift_info_id))
            if 'release' in request.form:
                slot.user = None
                slot.team = None
                db.session.commit()
                flash(f'Released slot in shift {slot.shift}.')
                return redirect(url_for('volunteering.shifts',
                                        task_id=task_id if task_id is not None else slot.shift.info.shift_info_id))
    form.populate(slot)
    return render_template('volunteering/slot.html', slot=slot, form=form)


@bp.route('/publish', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def publish():
    if request.method == 'POST':
        if len(request.form) > 0:
            for i in request.form:
                shift = Shift.query.get(int(i))
                shift.published = True
            db.session.commit()
            flash(f"Published {len(request.form)} shifts. These are now visible to others.")
        else:
            flash("No shifts were selected to publish.")
        return redirect(url_for('volunteering.publish'))
    all_tasks = ShiftInfo.query.order_by(ShiftInfo.name).all()
    shift_list = Shift.query.order_by(Shift.start_time).all()
    task_list = {task: [shift for shift in shift_list if shift.info == task] for task in all_tasks}
    count_list = {task: len([shift for shift in shift_list if shift.info == task and not shift.published])
                  for task in all_tasks}
    return render_template('volunteering/publish.html', shifts=shift_list, task_list=task_list, count_list=count_list)


@bp.route('/team_hours', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def team_hours():
    all_teams = Team.query.order_by(Team.name).all()
    all_teams = sorted([t for t in all_teams if t.is_active()], reverse=True,
                       key=lambda x: (x.name == TEAM_ORGANIZATION, x.name == TEAM_SUPER_VOLUNTEER))
    hours = {t: {'total': hours_delta(sum([s.duration() for s in ShiftSlot.query
                                          .filter(ShiftSlot.team == t, ShiftSlot.mandatory.is_(True)).all()],
                                          timedelta(0, 0))),
                 'assigned': hours_delta(sum([s.duration() for s in [slot for slot in ShiftSlot.query
                                             .filter(ShiftSlot.team == t, ShiftSlot.mandatory.is_(True)).all()
                                                                     if slot.user is not None]],
                                             timedelta(0, 0)))} for t in all_teams}
    return render_template('volunteering/team_hours.html', hours=hours)


@bp.route('/super_volunteers_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def super_volunteers_overview():
    all_super_volunteers = SuperVolunteer.query.order_by(SuperVolunteer.first_name).all()
    all_super_volunteers = [v for v in all_super_volunteers if v.user.team.name == TEAM_SUPER_VOLUNTEER]
    return render_template('volunteering/super_volunteers_overview.html', all_super_volunteers=all_super_volunteers)


@bp.route('/organization_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def organization_overview():
    all_super_volunteers = SuperVolunteer.query.order_by(SuperVolunteer.first_name).all()
    all_super_volunteers = [v for v in all_super_volunteers if v.user.team.name == TEAM_ORGANIZATION]
    return render_template('volunteering/organization_overview.html', all_super_volunteers=all_super_volunteers)


@bp.route('/user_volunteering_shifts', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[DANCER], ACCESS[SUPER_VOLUNTEER]])
def user_volunteering_shifts():
    if not g.ts.volunteering_system_open:
        flash("This page is not accessible yet.")
        return redirect(url_for('main.dashboard'))
    slots = ShiftSlot.query.filter(ShiftSlot.user == current_user).all()
    slots = sorted([s for s in slots if s.shift.published], key=lambda x: x.shift.start_time)
    now = datetime.now()
    return render_template('volunteering/user_volunteering_shifts.html', slots=slots, now=now)
