from ntds_webportal.base_functions import *
from flask import g, flash, render_template, current_app
from flask_login import current_user
from ntds_webportal import db
from ntds_webportal.models import Contestant, ContestantInfo, DancingInfo, VolunteerInfo, AdditionalInfo, \
    StatusInfo, PaymentInfo, MerchandiseInfo, User, Notification, SystemConfiguration
from ntds_webportal.data import *
from ntds_webportal.helper_classes import TeamFinancialOverview
import os


def get_dancing_categories(dancing_info):
    if dancing_info is None:
        return {cat: DancingInfo(competition=cat) for cat in ALL_COMPETITIONS}
    else:
        return {di.competition: di for di in dancing_info}


def notify_teamcaptains_couple_created(lead, follow, competition):
    teamcaptain_lead = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                         User.team == lead.contestant_info[0].team).first()
    text = "{dancer} has found a partner. He/She has signed up for {comp} with {partner} from team {team}."
    n = Notification(title=f"{lead} found a dancing partner for {competition}",
                     text=text.format(dancer=lead.get_full_name(), comp=competition,
                                      partner=follow.get_full_name(), team=follow.contestant_info[0].team.name),
                     user=teamcaptain_lead)
    db.session.add(n)
    teamcaptain_follow = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                           User.team == follow.contestant_info[0].team).first()
    n2 = Notification(title=f"{follow} found a dancing partner for {competition}",
                      text=text.format(dancer=follow.get_full_name(), comp=competition,
                                       partner=lead.get_full_name(), team=lead.contestant_info[0].team.name),
                      user=teamcaptain_follow)
    db.session.add(n2)
    db.session.commit()


def notify_teamcaptains_broken_up_couple(lead, follow, competition):
    teamcaptain_lead = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                         User.team == lead.contestant_info[0].team).first()
    text = "{dancer} no longer has a partner in {comp}."
    n = Notification(title=f"{lead.get_full_name()} no longer has a partner for {competition}",
                     text=text.format(dancer=lead.get_full_name(), comp=competition), user=teamcaptain_lead)
    db.session.add(n)
    teamcaptain_follow = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                           User.team == follow.contestant_info[0].team).first()
    n2 = Notification(title=f"{follow.get_full_name()} no longer has a partner for {competition}",
                      text=text.format(dancer=follow.get_full_name(), comp=competition), user=teamcaptain_follow)
    db.session.add(n2)
    db.session.commit()


def reset_tournament_state():
    g.ts.organizer_account_set = False
    g.ts.system_configured = False
    g.ts.website_accessible_to_teamcaptains = False
    g.ts.registration_period_started = False
    g.ts.registration_open = False
    g.ts.raffle_system_configured = False
    g.ts.main_raffle_taken_place = False
    g.ts.main_raffle_result_visible = False
    g.ts.numbers_rearranged = False
    g.ts.raffle_completed_message_sent = False
    db.session.commit()


def make_system_configuration_accessible_to_organizer():
    sc = SystemConfiguration.query.first()
    sc.system_configuration_accessible = True
    db.session.commit()
    flash("System configuration has been made accessible to the organizer.", "alert-success")


def get_total_dancer_price_list(dancer):
    price = TeamFinancialOverview(current_user)
    prices = price.prices()
    price = prices[dancer.contestant_info[0].student] + prices[dancer.merchandise_info[0].t_shirt]
    student_string = {STUDENT: 'Student', NON_STUDENT: 'Non-student', PHD_STUDENT: 'PhD-student'}
    description = f"{g.sc.tournament} {g.sc.city} {g.sc.year} - " \
                  f"{student_string[dancer.contestant_info[0].student]} entry fee"
    if dancer.merchandise_info[0].t_shirt != NO:
        description += " + t-shirt"
    if dancer.merchandise_info[0].mug:
        description += " + mug"
    if dancer.merchandise_info[0].bag:
        description += " + bag"
    paid_string = {True: "Yes", False: "No"}
    return [dancer.get_full_name(), price/100, description, paid_string[dancer.payment_info[0].all_paid()]]


def submit_contestant(form, contestant=None):
    new_dancer = True
    if contestant is None:
        contestant = Contestant()
        ci = ContestantInfo()
        di_ballroom = DancingInfo()
        di_ballroom.competition = BALLROOM
        di_latin = DancingInfo()
        di_latin.competition = LATIN
        vi = VolunteerInfo()
        ai = AdditionalInfo()
        si = StatusInfo()
        pi = PaymentInfo()
        mi = MerchandiseInfo()
        contestant.first_name = form.first_name.data.strip()
        contestant.prefixes = form.prefixes.data.strip() if form.prefixes.data.replace(' ', '') != '' else None
        contestant.last_name = form.last_name.data.strip()
        contestant.capitalize_name()
        ci.number = form.number.data
        ci.team = form.team.data
    else:
        ci = contestant.contestant_info[0]
        vi = contestant.volunteer_info[0]
        ai = contestant.additional_info[0]
        si = contestant.status_info[0]
        pi = contestant.payment_info[0]
        mi = contestant.merchandise_info[0]
        di_ballroom = contestant.competition(BALLROOM)
        di_latin = contestant.competition(LATIN)
        new_dancer = False
    contestant.email = form.email.data
    ci.contestant = contestant
    ci.student = form.student.data
    ci.first_time = str2bool(form.first_time.data)
    ci.diet_allergies = form.diet_allergies.data

    di_ballroom.contestant = contestant
    di_latin.contestant = contestant
    update_dancing_info(form, di_ballroom, di_latin)

    vi.contestant = contestant
    vi.volunteer = form.volunteer.data
    vi.first_aid = form.first_aid.data
    vi.emergency_response_officer = form.emergency_response_officer.data
    vi.jury_ballroom = form.jury_ballroom.data
    vi.jury_latin = form.jury_latin.data
    vi.license_jury_ballroom = form.license_jury_ballroom.data
    vi.license_jury_latin = form.license_jury_latin.data
    vi.level_ballroom = form.level_jury_ballroom.data
    vi.level_latin = form.level_jury_latin.data
    vi.jury_salsa = form.jury_salsa.data
    vi.jury_polka = form.jury_polka.data

    ai.contestant = contestant
    ai.sleeping_arrangements = str2bool(form.sleeping_arrangements.data)
    si.contestant = contestant
    pi.contestant = contestant

    mi.contestant = contestant
    mi.t_shirt = form.t_shirt.data
    mi.mug = str2bool(form.mug.data)
    mi.bag = str2bool(form.bag.data)

    if new_dancer:
        db.session.add(contestant)
        si.set_status(NO_GDPR)
    db.session.commit()
    return contestant


def update_dancing_info(form, di_ballroom, di_latin):
    di_ballroom.level = form.ballroom_level.data
    di_ballroom.role = form.ballroom_role.data
    db.session.add(di_ballroom)
    db.session.flush()
    if not str2bool(form.ballroom_blind_date.data) and form.ballroom_partner.data is not None:
        di_ballroom.set_partner(form.ballroom_partner.data.contestant_id)
    else:
        di_ballroom.set_partner(None)
    di_latin.level = form.latin_level.data
    di_latin.role = form.latin_role.data
    db.session.add(di_latin)
    db.session.flush()
    if not str2bool(form.latin_blind_date.data) and form.latin_partner.data is not None:
        di_latin.set_partner(form.latin_partner.data.contestant_id)
    else:
        di_latin.set_partner(None)


def submit_updated_dancing_info(form, contestant):
    di_ballroom = contestant.competition(BALLROOM)
    di_latin = contestant.competition(LATIN)
    update_dancing_info(form, di_ballroom, di_latin)
    db.session.commit()
    return contestant.get_full_name()


def generate_maintenance_page():
    maintenance_page = render_template('errors/502.html')
    dir_path = os.path.join(current_app.static_folder, '502.html')
    with open(dir_path, 'w') as the_file:
        the_file.write(maintenance_page)
    # maintenance_page = render_template('errors/502.html', render=True)
    # dir_path = os.path.join(current_app.root_path, current_app.template_folder)
    # dir_path = os.path.join(dir_path, '502.html')
    # with open(dir_path, 'w') as the_file:
    #     the_file.write(maintenance_page)
