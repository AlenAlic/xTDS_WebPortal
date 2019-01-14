from flask import render_template, redirect, url_for, flash, request, g, Markup
from flask_login import login_required, current_user
from ntds_webportal import db
from ntds_webportal.adjudication_system import bp
from ntds_webportal.adjudication_system.forms import SplitForm, EventForm, CompetitionForm, \
    CreateFirstRoundForm, DefaultCompetitionForm, ConfigureNextRoundForm, DanceForm, DisciplineForm, DancingClassForm, \
    PrintReportsForm, CoupleForm, DancerForm, EditDancerForm, EditCoupleForm, CreateAdjudicatorFromContestant, \
    CreateAdjudicatorFromSuperVolunteer
from ntds_webportal.models import requires_access_level, requires_adjudicator_access_level, Event, Competition, \
    DancingClass, Discipline, Dance, Round, RoundType, Adjudicator, Couple, CouplePresent, RoundResult, DanceActive, \
    Dancer, CompetitionMode, create_couples_list, ADJUDICATOR_SYSTEM_TABLES, DancingInfo, StatusInfo
from itertools import combinations
from ntds_webportal.data import *
from datetime import datetime, timedelta
import statistics
from sqlalchemy import or_


def reset():
    meta = db.metadata
    Competition.query.delete()
    Event.query.delete()
    for table in reversed(meta.sorted_tables):
        if table.name in ADJUDICATOR_SYSTEM_TABLES:
            print('Cleared table {}.'.format(table))
            db.session.execute(table.delete())
            db.session.execute("ALTER TABLE {} AUTO_INCREMENT = 1;".format(table.name))
    g.ts.dancers_imported = False
    g.ts.couples_imported = False
    db.session.commit()


def create_dances():
    Dance.query.delete()
    db.session.commit()
    for d in DANCES:
        dance = Dance()
        dance.name = d["name"]
        dance.tag = d["tag"]
        db.session.add(dance)
        db.session.commit()


def create_dancing_classes():
    DancingClass.query.delete()
    db.session.commit()
    for dc in DANCING_CLASSES:
        dancing_class = DancingClass()
        dancing_class.name = dc
        db.session.add(dancing_class)
        db.session.commit()


def create_disciplines():
    Discipline.query.delete()
    db.session.commit()
    for d in ALL_COMPETITIONS:
        discipline = Discipline()
        discipline.name = d
        db.session.add(discipline)
        db.session.commit()
    ballroom = Discipline.query.filter(Discipline.name == BALLROOM).first()
    ballroom.dances.extend(Dance.query.filter(Dance.name.in_(BALLROOM_DANCES)).all())
    latin = Discipline.query.filter(Discipline.name == LATIN).first()
    latin.dances.extend(Dance.query.filter(Dance.name.in_(LATIN_DANCES)).all())
    db.session.commit()


def create_base():
    create_dances()
    create_dancing_classes()
    create_disciplines()
    db.session.commit()


@bp.route('/event', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def event():
    event_form = EventForm()
    competition_form = CompetitionForm()
    default_form = DefaultCompetitionForm()
    if event_form.event_submit.name in request.form:
        if event_form.validate_on_submit():
            e = Event()
            e.name = event_form.name.data
            db.session.add(e)
            db.session.commit()
            flash(f"Created {e.name} event.")
            return redirect(url_for('adjudication_system.event'))
    if competition_form.comp_submit.name in request.form:
        if competition_form.validate_on_submit():
            c = Competition()
            c.discipline = competition_form.discipline.data
            c.dancing_class = competition_form.dancing_class.data
            c.floors = competition_form.floors.data
            c.when = competition_form.when.data
            c.event = g.event
            db.session.commit()
            flash(f"Created {c} competition.")
            return redirect(url_for('adjudication_system.event'))
    if default_form.default_submit.name in request.form:
        if default_form.validate_on_submit():
            create_base()
            start_time = datetime(default_form.when.data.year, default_form.when.data.month,
                                  default_form.when.data.day, 9, 0, 0)
            create_default_competition(BALLROOM, TEST, start_time)
            if default_form.beginners.data:
                create_default_competition(BALLROOM, BEGINNERS, start_time)
                create_default_competition(LATIN, BEGINNERS, start_time)
            if default_form.amateurs.data or default_form.professionals.data or \
                    default_form.masters.data or default_form.champions.data:
                create_default_competition(BALLROOM, BREITENSPORT_QUALIFICATION, start_time)
                create_default_competition(LATIN, BREITENSPORT_QUALIFICATION, start_time)
            if default_form.amateurs.data:
                create_default_competition(BALLROOM, AMATEURS, start_time)
                create_default_competition(LATIN, AMATEURS, start_time)
            if default_form.professionals.data:
                create_default_competition(BALLROOM, PROFESSIONALS, start_time)
                create_default_competition(LATIN, PROFESSIONALS, start_time)
            if default_form.masters.data:
                create_default_competition(BALLROOM, MASTERS, start_time)
                create_default_competition(LATIN, MASTERS, start_time)
            if default_form.champions.data:
                create_default_competition(BALLROOM, CHAMPIONS, start_time)
                create_default_competition(LATIN, CHAMPIONS, start_time)
            if default_form.closed.data:
                create_default_competition(BALLROOM, CLOSED, start_time)
                create_default_competition(LATIN, CLOSED, start_time)
            if default_form.open_class.data:
                create_default_competition(BALLROOM, OPEN_CLASS, start_time)
                create_default_competition(LATIN, OPEN_CLASS, start_time)
            flash(f"Created base dances, disciplines, classes, and the chosen default competitions.")
            return redirect(url_for('adjudication_system.event'))
    form = request.args
    if 'reset' in form:
        reset()
        flash('Tables reset')
        return redirect(url_for('adjudication_system.event'))
    return render_template('adjudication_system/event.html', event_form=event_form, competition_form=competition_form,
                           default_form=default_form)


def create_default_competition(disc, d_class, start_time):
    if disc == BALLROOM and (d_class == CLOSED or d_class == OPEN_CLASS):
        start_time = start_time + timedelta(days=1)
    if disc == LATIN and d_class != CLOSED and d_class != OPEN_CLASS:
        start_time = start_time + timedelta(days=1)
    time = start_time
    c = Competition()
    c.discipline = Discipline.query.filter(Discipline.name == disc).first()
    c.dancing_class = DancingClass.query.filter(DancingClass.name == d_class).first()
    c.mode = CompetitionMode.single_partner
    floors = 1
    if d_class == TEST:
        time = time + timedelta(hours=-1)
    if d_class == BREITENSPORT_QUALIFICATION:
        floors = 2
        time = time + timedelta(hours=1)
    if d_class == AMATEURS:
        time = time + timedelta(hours=2)
    if d_class == PROFESSIONALS:
        time = time + timedelta(hours=3)
    if d_class == MASTERS:
        time = time + timedelta(hours=4)
    if d_class == CHAMPIONS:
        time = time + timedelta(hours=5)
    if d_class == CLOSED:
        time = time + timedelta(hours=6)
    if d_class == OPEN_CLASS:
        time = time + timedelta(hours=7)
    c.floors = floors
    c.when = time
    c.event = g.event
    if d_class in BREITENSPORT_COMPETITIONS:
        c.qualification = Competition.query.join(DancingClass, Discipline)\
            .filter(DancingClass.name == BREITENSPORT_QUALIFICATION, Discipline.name == disc).first()
    db.session.commit()


@bp.route('/dances', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def dances():
    dance_form = DanceForm()
    if dance_form.dance_submit.name in request.form:
        if dance_form.validate_on_submit():
            check = Discipline.query.filter(or_(Dance.name == dance_form.name.data, Dance.tag == dance_form.tag.data))\
                .first()
            if check is None:
                d = Dance()
                d.name = dance_form.name.data
                d.tag = dance_form.tag.data
                db.session.add(d)
                db.session.commit()
                flash(f"Created {d.name} as a dance.")
                return redirect(url_for('adjudication_system.dances'))
            else:
                flash(f"Cannot create {dance_form.name.data} dance, a dance with that name or tag already exists.",
                      "alert-warning")
                return redirect(url_for('adjudication_system.dances'))
    all_dances = Dance.query.order_by(Dance.discipline_id, Dance.name).all()
    return render_template('adjudication_system/dances.html', dance_form=dance_form, all_dances=all_dances)


@bp.route('/edit_dance/<int:dance_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def edit_dance(dance_id):
    dance = Dance.query.filter(Dance.dance_id == dance_id).first()
    if dance is not None:
        dance_form = DanceForm()
        if request.method == "GET":
            dance_form.name.data = dance.name
            dance_form.tag.data = dance.tag
        if 'save_changes' in request.form:
            if dance_form.validate_on_submit():
                check = Discipline.query.filter(
                    or_(Dance.name == dance_form.name.data, Dance.tag == dance_form.tag.data)).first()
                if check is None:
                    dance.name = dance_form.name.data
                    dance.tag = dance_form.tag.data
                    db.session.commit()
                    flash(f"Edited {dance}.")
                    return redirect(url_for('adjudication_system.dances'))
                else:
                    flash(f"Cannot change {dance_form.name.data} dance, a dance with that name or tag already exists.",
                          "alert-warning")
                    return redirect(url_for('adjudication_system.edit_dance'))
        if 'delete_dance' in request.form:
            if dance.deletable():
                db.session.delete(dance)
                db.session.commit()
                flash(f"Deleted {dance}.")
                return redirect(url_for('adjudication_system.dances'))
            else:
                flash(f"Cannot delete {dance}, it has disciplines associated with it.")
                return redirect(url_for('adjudication_system.edit_dance'))
    else:
        flash("Invalid id.")
        return redirect(url_for('adjudication_system.dances'))
    return render_template('adjudication_system/edit_dance.html', dance_form=dance_form, dance=dance)


@bp.route('/disciplines', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def disciplines():
    discipline_form = DisciplineForm()
    if discipline_form.discipline_submit.name in request.form:
        if discipline_form.validate_on_submit():
            check = Discipline.query.filter(Discipline.name == discipline_form.name.data).first()
            if check is None:
                d = Discipline()
                d.name = discipline_form.name.data
                d.dances = Dance.query.filter(Dance.dance_id.in_(discipline_form.dances.data)).all()
                db.session.add(d)
                db.session.commit()
                flash(f"Created {d} as a discipline.")
                return redirect(url_for('adjudication_system.disciplines'))
            else:
                flash(f"Cannot create {discipline_form.name.data} discipline, it already exists.", "alert-warning")
                return redirect(url_for('adjudication_system.disciplines'))
    all_disciplines = Discipline.query.all()
    return render_template('adjudication_system/disciplines.html', discipline_form=discipline_form,
                           all_disciplines=all_disciplines)


@bp.route('/edit_discipline/<int:discipline_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def edit_discipline(discipline_id):
    discipline = Discipline.query.filter(Discipline.discipline_id == discipline_id).first()
    if discipline is not None:
        discipline_form = DisciplineForm(discipline)
        if 'save_changes' in request.form:
            if discipline_form.validate_on_submit():
                check = Discipline.query.filter(Discipline.name == discipline_form.name.data).first()
                if check is None:
                    discipline.name = discipline_form.name.data
                    discipline.dances = Dance.query.filter(Dance.dance_id.in_(discipline_form.dances.data)).all()
                    db.session.commit()
                    flash(f"Edited {discipline}.")
                    return redirect(url_for('adjudication_system.disciplines'))
                else:
                    flash(f"Cannot change name to {discipline_form.name.data}. A discipline with that name already "
                          f"exists.", "alert-warning")
                    return redirect(url_for('adjudication_system.edit_discipline'))
        if 'delete_discipline' in request.form:
            if discipline.deletable():
                db.session.delete(discipline)
                db.session.commit()
                flash(f"Deleted {discipline}.")
                return redirect(url_for('adjudication_system.disciplines'))
            else:
                flash(f"Cannot delete {discipline}, it has competitions associated with it.")
                return redirect(url_for('adjudication_system.edit_discipline'))
    else:
        flash("Invalid id.")
        return redirect(url_for('adjudication_system.disciplines'))
    return render_template('adjudication_system/edit_discipline.html', discipline_form=discipline_form,
                           discipline=discipline)


@bp.route('/dancing_classes', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def dancing_classes():
    dancing_class_form = DancingClassForm()
    if dancing_class_form.dancing_class_submit.name in request.form:
        if dancing_class_form.validate_on_submit():
            check = DancingClass.query.filter(DancingClass.name == dancing_class_form.name.data).first()
            if check is None:
                d = DancingClass()
                d.name = dancing_class_form.name.data
                db.session.add(d)
                db.session.commit()
                flash(f"Created {d} as a class.")
                return redirect(url_for('adjudication_system.dancing_classes'))
            else:
                flash(f"Cannot create {dancing_class_form.name.data} class, it already exists.", "alert-warning")
                return redirect(url_for('adjudication_system.dancing_classes'))
    all_classes = DancingClass.query.all()
    return render_template('adjudication_system/dancing_classes.html', dancing_class_form=dancing_class_form,
                           all_classes=all_classes)


@bp.route('/edit_dancing_class/<int:dancing_class_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def edit_dancing_class(dancing_class_id):
    dancing_class = DancingClass.query.filter(DancingClass.dancing_class_id == dancing_class_id).first()
    if dancing_class is not None:
        dancing_class_form = DancingClassForm()
        if request.method == "GET":
            dancing_class_form.name.data = dancing_class.name
        if 'save_changes' in request.form:
            if dancing_class_form.validate_on_submit():
                check = DancingClass.query.filter(DancingClass.name == dancing_class_form.name.data).first()
                if check is None:
                    dancing_class.name = dancing_class_form.name.data
                    db.session.commit()
                    flash(f"Edited {dancing_class}.")
                    return redirect(url_for('adjudication_system.dancing_classes'))
                else:
                    flash(f"Cannot change name to {dancing_class_form.name.data}. A class with that name already "
                          f"exists.", "alert-warning")
                    return redirect(url_for('adjudication_system.edit_dancing_class'))
        if 'delete_class' in request.form:
            if dancing_class.deletable():
                db.session.delete(dancing_class)
                db.session.commit()
                flash(f"Deleted {dancing_class}.")
                return redirect(url_for('adjudication_system.dancing_classes'))
            else:
                flash(f"Cannot delete {dancing_class}, it has competitions associated with it.")
                return redirect(url_for('adjudication_system.edit_dancing_class'))
    else:
        flash("Invalid id.")
        return redirect(url_for('adjudication_system.dancing_classes'))
    return render_template('adjudication_system/edit_dancing_class.html', dancing_class_form=dancing_class_form,
                           dancing_class=dancing_class)


@bp.route('/available_adjudicators', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER], ACCESS[ADJUDICATOR_ASSISTANT]])
def available_adjudicators():
    all_adjudicators = Adjudicator.query.order_by(Adjudicator.name).all()
    contestant_form = CreateAdjudicatorFromContestant()
    super_volunteer_form = CreateAdjudicatorFromSuperVolunteer()
    if request.method == POST:
        if contestant_form.adjudicator_contestant_submit.name in request.form:
            if contestant_form.validate_on_submit():
                contestant = contestant_form.contestant.data
                check_adjudicator = Adjudicator.query.filter(Adjudicator.user == contestant.user).first()
                if check_adjudicator is None:
                    adj = Adjudicator()
                    adj.name = contestant.get_full_name()
                    adj.tag = generate_tag(f"{contestant.first_name[:2]}{contestant.last_name[0]}".upper())
                    adj.user = contestant.user
                    contestant.volunteer_info.selected_adjudicator = True
                    db.session.add(adj)
                    db.session.commit()
                    flash(f"Added {contestant.get_full_name()} as an adjudicator", "alert-success")
                else:
                    flash(f"{contestant.get_full_name()} is already an adjudicator in the system.")
                return redirect(url_for("adjudication_system.available_adjudicators"))
        if super_volunteer_form.adjudicator_super_volunteer_submit.name in request.form:
            if super_volunteer_form.validate_on_submit():
                super_volunteer = super_volunteer_form.super_volunteer.data
                check_adjudicator = Adjudicator.query.filter(Adjudicator.user == super_volunteer.user).first()
                if check_adjudicator is None:
                    adj = Adjudicator()
                    adj.name = super_volunteer.get_full_name()
                    adj.tag = generate_tag(f"{super_volunteer.first_name[:2]}{super_volunteer.last_name[0]}".upper())
                    adj.user = super_volunteer.user
                    super_volunteer.selected_adjudicator = True
                    db.session.add(adj)
                    db.session.commit()
                    flash(f"Added {super_volunteer.get_full_name()} as an adjudicator", "alert-success")
                else:
                    flash(f"{super_volunteer.get_full_name()} is already an adjudicator in the system.")
                return redirect(url_for("adjudication_system.available_adjudicators"))
    return render_template('adjudication_system/available_adjudicators.html', all_adjudicators=all_adjudicators,
                           contestant_form=contestant_form, super_volunteer_form=super_volunteer_form)


def generate_tag(tag):
    original_tag = tag
    tags = [a.tag for a in Adjudicator.query.all()]
    for i in range(1, len(tags) + 1):
        if tag not in tags:
            break
        else:
            tag = f"{original_tag}{i}"
    return tag


@bp.route('/delete_adjudicator/<int:adjudicator_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def delete_adjudicator(adjudicator_id):
    adjudicator = Adjudicator.query.filter(Adjudicator.adjudicator_id == adjudicator_id).first()
    if adjudicator is not None:
        if adjudicator.user.is_dancer():
            adjudicator.user.dancer.volunteer_info.selected_adjudicator = False
        elif adjudicator.user.is_super_volunteer():
            adjudicator.user.super_volunteer.selected_adjudicator = False
        flash(f"Deleted {adjudicator} from the system.")
        db.session.delete(adjudicator)
        db.session.commit()
    else:
        flash(f"Invalid id.", "alert-warning")
    return redirect(url_for("adjudication_system.available_adjudicators"))


@bp.route('/adjudicator_assignments', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER], ACCESS[ADJUDICATOR_ASSISTANT]])
def adjudicator_assignments():
    if g.event is not None:
        all_adjudicators = Adjudicator.query.all()
        if request.method == "POST":
            form = request.form
            if 'save_assignments' in form:
                for comp in g.event.competitions:
                    if comp.is_configurable():
                        checks = [a for a in [f"{comp.competition_id}-{adj.adjudicator_id}" for adj in all_adjudicators]
                                  if a in form]
                        adjudicators = [int(a) for a in [a.split('-')[1] for a in checks]]
                        comp.adjudicators = Adjudicator.query.filter(Adjudicator.adjudicator_id.in_(adjudicators)).all()
                db.session.commit()
                flash("Saved assignments", "alert-success")
    else:
        flash("There is no event yet for adjudicators to be assigned to.")
        return redirect(url_for("main.dashboard"))
    return render_template('adjudication_system/adjudicator_assignments.html', all_adjudicators=all_adjudicators)


@bp.route('/available_dancers', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def available_dancers():
    form = DancerForm()
    if request.method == POST:
        if form.submit.name in request.form:
            if form.validate_on_submit():
                contestant = form.contestant.data
                check_dancer = Dancer.query.filter(Dancer.name == contestant.get_full_name(),
                                                   Dancer.number == contestant.contestant_info.number,
                                                   Dancer.role == form.role.data).first()
                if check_dancer is None:
                    dancer = Dancer()
                    dancer.name = contestant.get_full_name()
                    dancer.number = contestant.contestant_info.number
                    dancer.role = form.role.data
                    dancer.team = contestant.contestant_info.team_name()
                    db.session.add(dancer)
                    db.session.commit()
                    flash(f"Created {dancer.name} ({dancer.number}) as a {dancer.role}", "alert-success")
                else:
                    flash(f"{check_dancer.name} as a {form.role.data} is already in the system.")
                return redirect(url_for("adjudication_system.available_dancers"))
    if request.method == GET:
        if "import_dancers" in request.args:
            all_contestant_dancers = DancingInfo.query\
                .join(StatusInfo, DancingInfo.contestant_id == StatusInfo.contestant_id)\
                .filter(StatusInfo.status == CONFIRMED, DancingInfo.level != NO).all()
            added_dancers = []
            for dancing_info in all_contestant_dancers:
                check_dancer = Dancer.query.filter(Dancer.name == dancing_info.contestant.get_full_name(),
                                                   Dancer.number == dancing_info.contestant.contestant_info.number,
                                                   Dancer.role == dancing_info.role).first()
                disc = Discipline.query.filter(Discipline.name == dancing_info.competition).first()
                if dancing_info.level == BREITENSPORT:
                    dc = BREITENSPORT_QUALIFICATION
                else:
                    dc = dancing_info.level
                dancing_class = DancingClass.query.filter(DancingClass.name == dc).first()
                comp = Competition.query.filter(Competition.discipline == disc,
                                                Competition.dancing_class == dancing_class).first()
                if check_dancer is None:
                    dancer = Dancer()
                    dancer.name = dancing_info.contestant.get_full_name()
                    dancer.number = dancing_info.contestant.contestant_info.number
                    dancer.role = dancing_info.role
                    dancer.team = dancing_info.contestant.contestant_info.team_name()
                    dancer.contestant = dancing_info.contestant
                    dancer.append_competition(comp)
                    db.session.add(dancer)
                    added_dancers.append(dancer.name)
                else:
                    check_dancer.append_competition(comp)
            g.ts.dancers_imported = True
            db.session.commit()
            flash(f"Imported {len(added_dancers)} new dancers into the system.")
            return redirect(url_for("adjudication_system.available_dancers"))
    dancers = Dancer.query.all()
    return render_template('adjudication_system/available_dancers.html', form=form, dancers=dancers)


@bp.route('/edit_dancer/<int:dancer_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def edit_dancer(dancer_id):
    dancer = Dancer.query.filter(Dancer.dancer_id == dancer_id).first()
    if dancer is not None:
        form = EditDancerForm(dancer)
        if 'save_changes' in request.form:
            if form.validate_on_submit():
                comps = Competition.query.filter(Competition.competition_id.in_(form.competitions.data)).all()
                dancer.set_competitions(comps)
                db.session.commit()
                flash(f"Edited {dancer} ({dancer.role}).")
                return redirect(url_for('adjudication_system.available_dancers'))
    else:
        flash("Invalid id.")
        return redirect(url_for('adjudication_system.available_dancers'))
    return render_template('adjudication_system/edit_dancer.html', form=form, dancer=dancer)


@bp.route('/available_couples', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def available_couples():
    form = CoupleForm()
    if request.method == POST:
        if form.submit.name in request.form:
            if form.validate_on_submit():
                check_couple = Couple.query.filter(Couple.lead == form.lead.data, Couple.follow == form.follow.data)\
                    .first()
                if check_couple is None:
                    couple = Couple()
                    couple.lead = form.lead.data
                    couple.follow = form.follow.data
                    couple.number = form.lead.data.number
                    couple.competitions = Competition.query\
                        .filter(Competition.competition_id.in_(form.competitions.data)).all()
                    db.session.add(couple)
                    db.session.commit()
                    flash(f"Created couple with {form.lead.data} as lead and {form.follow.data} as follow in the "
                          f"following competitions: {', '.join([c.__repr__() for c in couple.competitions])}.",
                          "alert-success")
                else:
                    flash(f"{form.lead.data} and {form.follow.data} are already a couple.")
                return redirect(url_for("adjudication_system.available_couples"))
    if request.method == GET:
        if "import_couples" in request.args:
            all_leads = DancingInfo.query\
                .join(StatusInfo, DancingInfo.contestant_id == StatusInfo.contestant_id)\
                .filter(StatusInfo.status == CONFIRMED, DancingInfo.level != NO, DancingInfo.partner.isnot(None),
                        DancingInfo.role == LEAD).all()
            added_couples = []
            for lead in all_leads:
                follow = DancingInfo.query.join(StatusInfo, DancingInfo.contestant_id == StatusInfo.contestant_id)\
                    .filter(StatusInfo.status == CONFIRMED, DancingInfo.role == OPPOSITE_ROLES[lead.role],
                            DancingInfo.level == lead.level, DancingInfo.partner == lead.contestant_id,
                            DancingInfo.competition == lead.competition).first()
                if follow is not None:
                    check_lead = Dancer.query.filter(Dancer.name == lead.contestant.get_full_name(),
                                                     Dancer.number == lead.contestant.contestant_info.number,
                                                     Dancer.role == lead.role).first()
                    check_follow = Dancer.query.filter(Dancer.name == follow.contestant.get_full_name(),
                                                       Dancer.number == follow.contestant.contestant_info.number,
                                                       Dancer.role == follow.role).first()
                    disc = Discipline.query.filter(Discipline.name == lead.competition).first()
                    if lead.level == BREITENSPORT:
                        dc = BREITENSPORT_QUALIFICATION
                    else:
                        dc = lead.level
                    dancing_class = DancingClass.query.filter(DancingClass.name == dc).first()
                    if check_lead is not None and check_follow is not None:
                        check_couple = Couple.query.filter(Couple.lead == check_lead, Couple.follow == check_follow)\
                            .first()
                        if check_couple is None:
                            couple = Couple()
                            couple.number = check_lead.number
                            couple.lead = check_lead
                            couple.follow = check_follow
                            if disc is not None and dancing_class is not None:
                                comp = Competition.query.filter(Competition.discipline == disc,
                                                                Competition.dancing_class == dancing_class).first()
                                if comp.mode == CompetitionMode.single_partner:
                                    couple.competitions.append(comp)
                            db.session.add(couple)
                            added_couples.append(couple)
                        else:
                            if disc is not None and dancing_class is not None:
                                comp = Competition.query.filter(Competition.discipline == disc,
                                                                Competition.dancing_class == dancing_class).first()
                                if comp.mode == CompetitionMode.single_partner:
                                    if comp not in check_couple.competitions:
                                        check_couple.competitions.append(comp)
            couples_to_delete = Couple.query.all()
            couples_to_delete = [c for c in couples_to_delete if len(c.competitions) == 0]
            for c in couples_to_delete:
                db.session.delete(c)
            g.ts.couples_imported = True
            db.session.commit()
            flash(f"Imported {len(added_couples)} new couples into the system.")
            return redirect(url_for("adjudication_system.available_couples"))
    couples = Couple.query.all()
    return render_template('adjudication_system/available_couples.html', form=form, couples=couples)


@bp.route('/edit_couple/<int:couple_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def edit_couple(couple_id):
    couple = Couple.query.filter(Couple.couple_id == couple_id).first()
    if couple is not None:
        form = EditCoupleForm(couple)
        if 'save_changes' in request.form:
            if form.validate_on_submit():
                couple.competitions = Competition.query\
                    .filter(Competition.competition_id.in_(form.competitions.data)).all()
                db.session.commit()
                flash(f"Couple data {couple.lead}, {couple.follow} updated.")
                return redirect(url_for('adjudication_system.available_couples'))
    else:
        flash("Invalid id.")
        return redirect(url_for('adjudication_system.available_couples'))
    return render_template('adjudication_system/edit_couple.html', form=form, couple=couple)


@bp.route('/delete_couple/<int:couple_id>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def delete_couple(couple_id):
    couple = Couple.query.filter(Couple.couple_id == couple_id).first()
    if couple is not None:
        if couple.deletable():
            flash(f"Deleted {couple.lead} and {couple.follow} as a couple from the system.")
            db.session.delete(couple)
            db.session.commit()
        else:
            flash("Cannot delete couple.")
    else:
        flash(f"Invalid id.", "alert-warning")
    return redirect(url_for("adjudication_system.available_couples"))


@bp.route('/competition', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def competition():
    competition_id = request.args.get('competition_id', type=int)
    comp = Competition.query.filter(Competition.competition_id == competition_id).first()
    if comp is None:
        return redirect(url_for("adjudication_system.event"))
    if len(comp.rounds) > 0 and comp.has_adjudicators():
        if not (len(comp.rounds) == 1 and len(comp.rounds[0].heats) == 0):
            return redirect(url_for("adjudication_system.progress", round_id=comp.last_round().round_id))
    competition_form = CompetitionForm(comp)
    round_form = CreateFirstRoundForm(comp)
    if competition_form.comp_submit.name in request.form:
        if competition_form.validate_on_submit():
            comp.dancing_class = competition_form.dancing_class.data
            comp.discipline = competition_form.discipline.data
            comp.floors = competition_form.floors.data
            comp.when = competition_form.when.data
            comp.qualification = competition_form.qualification.data
            comp.mode = competition_form.mode.data
            comp.adjudicators = Adjudicator.query \
                .filter(Adjudicator.adjudicator_id.in_(competition_form.adjudicators.data)).all()
            comp.couples = Couple.query.filter(Couple.couple_id.in_(competition_form.competition_couples.data)).all()
            comp.leads = Dancer.query.filter(Dancer.dancer_id.in_(competition_form.competition_leads.data)).all()
            comp.follows = Dancer.query.filter(Dancer.dancer_id.in_(competition_form.competition_follows.data)).all()
            db.session.commit()
            flash(f"Changes to {comp} saved.", "alert-success")
            return redirect(url_for("adjudication_system.competition", competition_id=comp.competition_id))
    if round_form.round_submit.name in request.form:
        if round_form.validate_on_submit():
            r = Round()
            r.type = round_form.type.data
            r.min_marks = round_form.min_marks.data
            r.max_marks = max(round_form.min_marks.data, round_form.max_marks.data)
            r.is_active = False
            r.competition = comp
            r.dances = Dance.query.filter(Dance.dance_id.in_(round_form.dances.data)).all()
            for dance in r.dances:
                da = DanceActive()
                da.round = r
                da.dance = dance
                r.dance_active.append(da)
            r.couples = comp.generate_couples()
            r.create_heats(round_form.heats.data)
            db.session.commit()
            flash(f"Created {r.type.value} for {comp}.", "alert-success")
            return redirect(url_for("adjudication_system.progress", round_id=r.round_id))
    return render_template('adjudication_system/competition.html', competition=comp, competition_form=competition_form,
                           round_form=round_form)


@bp.route('/progress', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def progress():
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("adjudication_system.event"))
    if not dancing_round.has_adjudicators():
        flash(f"Please assign adjudicators first.", "alert-warning")
        return redirect(url_for("adjudication_system.competition",
                                competition_id=dancing_round.competition.competition_id))
    if dancing_round.first_round_after_qualification_split():
        round_form = CreateFirstRoundForm(dancing_round.competition)
    else:
        round_form = ConfigureNextRoundForm(dancing_round)
    if request.method == 'POST':
        if "split" in request.form:
            return redirect(url_for("adjudication_system.split", round_id=dancing_round.round_id))
        if "configure" in request.form:
            if round_form.validate_on_submit():
                if dancing_round.first_round_after_qualification_split():
                    couples = [c for c in dancing_round.couples if str(c.couple_id) in request.form]
                    dancing_round.type = round_form.type.data
                    dancing_round.min_marks = round_form.min_marks.data
                    dancing_round.max_marks = max(round_form.min_marks.data, round_form.max_marks.data)
                    dancing_round.is_active = False
                    dancing_round.dances = Dance.query.filter(Dance.dance_id.in_(round_form.dances.data)).all()
                    for dance in dancing_round.dances:
                        da = DanceActive()
                        da.round = dancing_round
                        da.dance = dance
                        dancing_round.dance_active.append(da)
                    dancing_round.couples = couples
                    dancing_round.create_heats(round_form.heats.data)
                    db.session.commit()
                    flash(f"Configured {dancing_round.type.value} for {dancing_round.competition}.", "alert-success")
                    return redirect(url_for("adjudication_system.progress", round_id=dancing_round.round_id))
                if dancing_round.competition.is_change_per_dance():
                    dancers = dancing_round.change_per_dance_dancers_rows()
                    if round_form.type.data != RoundType.re_dance.name:
                        dancers = [d for d in dancers if d['crosses'] >= round_form.cutoff.data or d['crosses'] == -1]
                    else:
                        dancers = [d for d in dancers if d['crosses'] < round_form.cutoff.data]
                    dancers = [d['dancer'] for d in dancers if str(d['dancer'].dancer_id) in request.form]
                    leads = [d for d in dancers if d.role == LEAD]
                    follows = [d for d in dancers if d.role == FOLLOW]
                    if len(leads) == len(follows):
                        couples = create_couples_list(leads=leads, follows=follows)
                    else:
                        flash(f"Cannot configure the next round {len(leads)} leads and {len(follows)} follows. "
                              f"Please check the list again.", "alert-warning")
                        return render_template('adjudication_system/progress.html', dancing_round=dancing_round,
                                               round_form=round_form)
                else:
                    if dancing_round.is_final():
                        couples = [c for c in dancing_round.couples if str(c.couple_id) in request.form]
                    else:
                        couples = [r for r in dancing_round.round_results if str(r.couple.couple_id) in request.form]
                        if round_form.type.data != RoundType.re_dance.name:
                            couples = [r.couple for r in couples if r.marks >= round_form.cutoff.data or r.marks == -1]
                        else:
                            couples = [r.couple for r in couples if r.marks < round_form.cutoff.data]
                r = Round()
                r.type = round_form.type.data
                r.min_marks = round_form.min_marks.data
                r.max_marks = max(round_form.min_marks.data, round_form.max_marks.data)
                r.is_active = False
                r.competition = dancing_round.competition
                r.dances = Dance.query.filter(Dance.dance_id.in_(round_form.dances.data)).all()
                for dance in r.dances:
                    da = DanceActive()
                    da.round = r
                    da.dance = dance
                    r.dance_active.append(da)
                if dancing_round.competition.mode == CompetitionMode.change_per_round:
                    round_couples = create_couples_list(couples=couples)
                else:
                    round_couples = couples
                r.couples = round_couples
                if round_form.type.data == RoundType.final.name:
                    r.create_final()
                else:
                    r.create_heats(round_form.heats.data)
                db.session.commit()
                flash(f"Created {r.type.value} for {dancing_round.competition}.", "alert-success")
                return redirect(url_for("adjudication_system.progress", round_id=r.round_id))
        if "delete" in request.form:
            comp = dancing_round.competition
            flash(f"Deleted {dancing_round}.")
            db.session.delete(dancing_round)
            db.session.commit()
            try:
                return redirect(url_for("adjudication_system.progress", round_id=comp.last_round().round_id))
            except AttributeError:
                return redirect(url_for("adjudication_system.competition", competition_id=comp.competition_id))
    return render_template('adjudication_system/progress.html', dancing_round=dancing_round, round_form=round_form)


def split_breitensport(dancing_round, chosen_split):
    competitions = [c for c in dancing_round.competition.qualifications]
    competitions.sort(key=lambda comp: comp.when)
    for idx, dc in enumerate(chosen_split):
        competitions[idx].couples.extend(chosen_split[idx])
        db.session.commit()


# noinspection PyTypeChecker
def split_couples_into_competitions(dancing_round):
    num_comps = len(dancing_round.competition.qualifications)
    round_result_list = [r.marks for r in dancing_round.round_results]
    unique_results = list(set(round_result_list))
    unique_results.sort()
    combs = []
    for c in combinations(range(1, len(unique_results)), num_comps - 1):
        combs.append(split_list(unique_results, list(c)))
    splittings = [[[] for _ in range(num_comps)] for _ in combs]
    for i in range(len(combs)):
        for j in range(num_comps):
            for r in dancing_round.round_results:
                if r.marks in combs[i][j]:
                    splittings[i][j].append(r.couple)
    splittings.sort(key=lambda x: statistics.stdev([len(s) for s in x]))
    splitting_strings = [' / '.join([str(st) for st in s]) for s in [[len(l) for l in sp] for sp in splittings]]
    splitting_results = {}
    for i in range(len(combs)):
        splitting_results.update({splitting_strings[i]: splittings[i]})
    return splitting_results


def split_list(l, indices):
    container = [l[:indices[0]]]
    for idx in range(len(indices)-1):
        container.append(l[indices[idx]:indices[idx+1]])
    container.append(l[indices[-1]:])
    return container


@bp.route('/split', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def split():
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("adjudication_system.event"))
    if dancing_round.is_split():
        return redirect(url_for("adjudication_system.progress", round_id=dancing_round.round_id))
    if len(dancing_round.competition.qualifications) == 1:
        flash("There is only one competition to qualify for. Cannot split couples. Please add a second qualification.")
        return redirect(url_for("adjudication_system.progress", round_id=dancing_round.round_id))
    form = SplitForm(split_couples_into_competitions(dancing_round))
    if form.validate_on_submit():
        split_breitensport(dancing_round, split_couples_into_competitions(dancing_round)[form.scenarios.data])
        flash(f"{dancing_round} split!", "alert-success")
        return redirect(url_for("adjudication_system.progress", round_id=dancing_round.round_id))
    return render_template('adjudication_system/split.html', dancing_round=dancing_round, form=form)


@bp.route('/reports', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def reports():
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("adjudication_system.event"))
    if dancing_round.first_dance() is None:
        flash('Please configure the dancing round first.', "alert-warning")
        return redirect(url_for('adjudication_system.progress', round_id=dancing_round.round_id))
    form = PrintReportsForm()
    return render_template('adjudication_system/reports.html', dancing_round=dancing_round, form=form)


@bp.route('/reports_print', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def reports_print():
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("adjudication_system.event"))
    form = PrintReportsForm()
    return render_template('adjudication_system/reports_print.html', dancing_round=dancing_round, form=form)


@bp.route('/floor_management', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def floor_management():
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("adjudication_system.event"))
    dance_id = request.args.get('dance_id', 0, type=int)
    if dance_id == 0:
        if dancing_round.has_dances():
            return redirect(url_for('adjudication_system.floor_management', round_id=dancing_round.round_id,
                                    dance_id=dancing_round.first_dance().dance_id))
        else:
            flash('Please configure the dancing round first.', "alert-warning")
            return redirect(url_for('adjudication_system.progress', round_id=dancing_round.round_id))
    elif not dancing_round.has_dance(dance_id):
        return redirect(url_for('adjudication_system.floor_management', round_id=dancing_round.round_id,
                                dance_id=dancing_round.first_dance().dance_id))
    dance = Dance.query.get(dance_id)
    if request.method == 'POST':
        if "save" in request.form:
            for present_id in request.form:
                try:
                    cp = CouplePresent.query.get(present_id)
                    cp.present = True
                except AttributeError:
                    pass
        elif "refresh" in request.form:
            pass
        else:
            presents = [heat.couples_present for heat in dancing_round.heats
                        if heat.dance_id == int([f for f in request.form][0])]
            for l in presents:
                for cp in l:
                    cp.present = False
        db.session.commit()
    return render_template('adjudication_system/floor_management.html', dancing_round=dancing_round, dance=dance)


@bp.route('/adjudication', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def adjudication():
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("adjudication_system.event"))
    dance_id = request.args.get('dance_id', 0, type=int)
    if dance_id == 0:
        if dancing_round.has_dances():
            return redirect(url_for('adjudication_system.adjudication', round_id=dancing_round.round_id,
                                    dance_id=dancing_round.first_dance().dance_id))
        else:
            flash('Please configure the dancing round first.', "alert-warning")
            return redirect(url_for('adjudication_system.progress', round_id=dancing_round.round_id))
    elif not dancing_round.has_dance(dance_id):
        return redirect(url_for('adjudication_system.adjudication', round_id=dancing_round.round_id,
                                dance_id=dancing_round.first_dance().dance_id))
    dance = Dance.query.get(dance_id)
    if request.method == 'POST':
        if "evaluate" in request.form:
            dancing_round.deactivate()
            if not dancing_round.is_final():
                if dancing_round.can_evaluate():
                    couple_marks = {}
                    couples = dancing_round.couples
                    for couple in couples:
                        marks = [heat.marks for heat in dancing_round.heats]
                        count = 0
                        for mark in marks:
                            for m in mark:
                                if m.mark and m.couple == couple:
                                    count += 1
                        couple_marks.update({couple: count})
                    previous_round = dancing_round.previous_round()
                    direct_qualified_couples = []
                    if dancing_round.type == RoundType.re_dance:
                        max_mark = max(couple_marks.values()) + 1
                        if dancing_round.competition.is_change_per_dance():
                            direct_qualified_couples = [c for c in previous_round.couples if c.number
                                                        not in [c.number for c in couples]]
                        else:
                            direct_qualified_couples = [c for c in previous_round.couples if c.number
                                                        not in [c.number for c in couples]]
                        for couple in direct_qualified_couples:
                            couple_marks.update({couple: max_mark})
                    for couple in couples + direct_qualified_couples:
                        result = RoundResult()
                        result.couple = couple
                        result.marks = couple_marks[couple]
                        result.round = dancing_round
                    round_result_list = [r.marks for r in dancing_round.round_results]
                    unique_results = list(set(round_result_list))
                    unique_results.sort(reverse=True)
                    result_placing = {}
                    for i in set(round_result_list):
                        result_placing.update({i: round_result_list.count(i)})
                    result_map = {}
                    counter = 1
                    for i in unique_results:
                        if result_placing[i] == 1:
                            result_map.update({i: str(counter)})
                        else:
                            result_map.update({i: str(counter) + ' - ' + str(counter+result_placing[i]-1)})
                        counter += result_placing[i]
                    for result in dancing_round.round_results:
                        result.placing = result_map[result.marks]
                    if dancing_round.type == RoundType.re_dance:
                        for result in dancing_round.round_results:
                            if result.couple in direct_qualified_couples:
                                result.marks = -1
                    db.session.commit()
                    return redirect(url_for("adjudication_system.progress",
                                            round_id=request.args.get('round_id', type=int)))
                else:
                    flash(Markup(f"Cannot evaluate round.<br/><br/>{'<br/>'.join(dancing_round.evaluation_errors())}"),
                          "alert-danger")
            else:
                if dancing_round.is_completed():
                    flash('Final evaluated.', 'alert-success')
                else:
                    flash('Cannot evaluate the final. Please check the placings.')
        if 'save_marks' in request.form:
            if not dancing_round.is_dance_active(dance):
                for mark in dancing_round.marks(dance):
                    mark.mark = str(mark.mark_id) in request.form
                db.session.commit()
                flash(f'Placings for {dancing_round} - {dance} saved.')
            else:
                flash('Cannot change marks when a dance is being adjudicated.', 'alert-warning')
            return redirect(url_for("adjudication_system.adjudication", round_id=request.args.get('round_id', type=int),
                                    dance_id=dance.dance_id))
        if 'save_final_placings' in request.form:
            if not dancing_round.is_dance_active(dance):
                for placing in [p for p in dancing_round.final_placings if p.dance == dance]:
                    try:
                        placing.final_placing = int(request.form[str(placing.final_placing_id)])
                    except ValueError:
                        placing.final_placing = 0
                db.session.commit()
                flash(f'Placings for {dancing_round} - {dance} saved.')
            else:
                flash('Cannot change marks when a dance is being adjudicated.', 'alert-warning')
            return redirect(url_for("adjudication_system.adjudication", round_id=request.args.get('round_id', type=int),
                                    dance_id=dance.dance_id))
    return render_template('adjudication_system/adjudication.html', dancing_round=dancing_round, dance=dance)


@bp.route('/final_result', methods=['GET'])
@login_required
@requires_access_level([ACCESS[TOURNAMENT_OFFICE_MANAGER]])
def final_result():
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("adjudication_system.event"))
    skating = dancing_round.skating_summary()
    return render_template('adjudication_system/final_result.html', dancing_round=dancing_round, skating=skating)


@bp.route('/adjudicator_dashboard', methods=['GET'])
@login_required
@requires_adjudicator_access_level
def adjudicator_dashboard():
    if g.sc.check_in_accessible():
        current_user.adjudicator.round = 0
        current_user.adjudicator.dance = 0
        db.session.commit()
    else:
        flash('Adjudication assignments are not accessible yet.')
        return redirect(url_for("main.dashboard"))
    return render_template('adjudication_system/adjudicator_dashboard.html')


@bp.route('/adjudicate_start_page', methods=['GET'])
@login_required
@requires_adjudicator_access_level
def adjudicate_start_page():
    current_user.adjudicator.round = 0
    current_user.adjudicator.dance = 0
    db.session.commit()
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("adjudication_system.adjudicator_dashboard"))
    if not dancing_round.is_active:
        flash(f"{dancing_round.competition} is currently closed.")
        return redirect(url_for("adjudication_system.adjudicator_dashboard"))
    return render_template('adjudication_system/adjudicate_start_page.html', dancing_round=dancing_round)


@bp.route('/adjudicate', methods=['GET'])
@login_required
@requires_adjudicator_access_level
def adjudicate():
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("main.dashboard"))
    if not dancing_round.is_active:
        flash(f"{dancing_round.competition} is currently closed.")
        return redirect(url_for("main.dashboard"))
    dance_id = request.args.get('dance_id', 0, type=int)
    if dance_id == 0:
        return redirect(url_for('adjudication_system.adjudicate', round_id=dancing_round.round_id,
                                dance_id=dancing_round.first_dance().dance_id))
    dance = Dance.query.get(dance_id)
    current_user.adjudicator.round = dancing_round_id
    current_user.adjudicator.dance = dance_id
    db.session.commit()
    return render_template('adjudication_system/adjudicate.html', dancing_round=dancing_round, dance=dance)


@bp.route('/floor_manager_start_page', methods=['GET'])
@login_required
@requires_access_level([ACCESS[FLOOR_MANAGER]])
def floor_manager_start_page():
    return render_template('adjudication_system/floor_manager_start_page.html')


@bp.route('/floor_manager', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[FLOOR_MANAGER]])
def floor_manager():
    dancing_round_id = request.args.get('round_id', 0, type=int)
    dancing_round = Round.query.filter(Round.round_id == dancing_round_id).first()
    if dancing_round is None:
        return redirect(url_for("adjudication_system.floor_manager_start_page"))
    dance_id = request.args.get('dance_id', 0, type=int)
    if dance_id == 0:
        if dancing_round.has_dances():
            return redirect(url_for('adjudication_system.floor_manager', round_id=dancing_round.round_id,
                                    dance_id=dancing_round.first_dance().dance_id))
        else:
            return redirect(url_for('adjudication_system.floor_manager_start_page', round_id=dancing_round.round_id))
    elif not dancing_round.has_dance(dance_id):
        return redirect(url_for('adjudication_system.floor_manager', round_id=dancing_round.round_id,
                                dance_id=dancing_round.first_dance().dance_id))
    dance = Dance.query.get(dance_id)
    return render_template('adjudication_system/floor_manager.html', dancing_round=dancing_round, dance=dance)
