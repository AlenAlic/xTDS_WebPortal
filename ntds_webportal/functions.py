from ntds_webportal.util import *
from flask import g, flash, render_template, current_app
from flask_login import current_user
from ntds_webportal import db
from ntds_webportal.models import Contestant, ContestantInfo, DancingInfo, VolunteerInfo, AdditionalInfo, \
    StatusInfo, PaymentInfo, MerchandiseInfo, User, Notification, SystemConfiguration, Team
from ntds_webportal.data import *
import sqlalchemy as alchemy
import os


def active_teams():
    teams = Team.query.filter(Team.name != TEAM_SUPER_VOLUNTEER, Team.name != TEAM_ORGANIZATION).all()
    return list(sorted([t for t in teams if t.is_active()], key=lambda x: x.display_name()))


def database_is_empty():
    table_names = alchemy.inspect(db.engine).get_table_names()
    is_empty = table_names == []
    print('Database empty: {is_empty}.'.format(is_empty=is_empty))
    return is_empty


def get_dancing_categories(dancing_info):
    if dancing_info is None:
        return {cat: DancingInfo(competition=cat) for cat in ALL_COMPETITIONS}
    else:
        return {di.competition: di for di in dancing_info}


def notify_teamcaptains_couple_created(lead, follow, competition):
    teamcaptain_lead = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                         User.team == lead.contestant_info.team).first()
    text = "{dancer} has found a partner. He/She has signed up for {comp} with {partner} from team {team}."
    n = Notification(title=f"{lead} found a dancing partner for {competition}",
                     text=text.format(dancer=lead.get_full_name(), comp=competition,
                                      partner=follow.get_full_name(), team=follow.contestant_info.team.name),
                     user=teamcaptain_lead)
    n.send()
    teamcaptain_follow = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                           User.team == follow.contestant_info.team).first()
    n2 = Notification(title=f"{follow} found a dancing partner for {competition}",
                      text=text.format(dancer=follow.get_full_name(), comp=competition,
                                       partner=lead.get_full_name(), team=lead.contestant_info.team.name),
                      user=teamcaptain_follow)
    n2.send()


def notify_teamcaptains_broken_up_couple(lead, follow, competition):
    teamcaptain_lead = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                         User.team == lead.contestant_info.team).first()
    text = "{dancer} no longer has a partner in {comp}."
    n = Notification(title=f"{lead.get_full_name()} no longer has a partner for {competition}",
                     text=text.format(dancer=lead.get_full_name(), comp=competition), user=teamcaptain_lead)
    n.send()
    teamcaptain_follow = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                           User.team == follow.contestant_info.team).first()
    n2 = Notification(title=f"{follow.get_full_name()} no longer has a partner for {competition}",
                      text=text.format(dancer=follow.get_full_name(), comp=competition), user=teamcaptain_follow)
    n2.send()


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
    g.ts.merchandise_finalized = False
    g.ts.super_volunteer_registration_open = False
    g.ts.volunteering_system_open = False
    g.ts.dancers_imported = False
    g.ts.couples_imported = False
    db.session.commit()


def make_system_configuration_accessible_to_organizer():
    sc = SystemConfiguration.query.first()
    sc.system_configuration_accessible = True
    db.session.commit()
    flash("System configuration has been made accessible to the organizer.", "alert-success")


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
        ci.team = current_user.team
    else:
        ci = contestant.contestant_info
        vi = contestant.volunteer_info
        ai = contestant.additional_info
        si = contestant.status_info
        pi = contestant.payment_info
        mi = contestant.merchandise_info
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
    if form.jury_ballroom.data == NO:
        vi.not_adjudicating(BALLROOM)
    else:
        vi.jury_ballroom = form.jury_ballroom.data
        vi.license_jury_ballroom = form.license_jury_ballroom.data
        vi.level_ballroom = form.level_jury_ballroom.data
    if form.jury_latin.data == NO:
        vi.not_adjudicating(LATIN)
    else:
        vi.jury_latin = form.jury_latin.data
        vi.license_jury_latin = form.license_jury_latin.data
        vi.level_latin = form.level_jury_latin.data
    vi.jury_salsa = form.jury_salsa.data
    vi.jury_polka = form.jury_polka.data

    ai.contestant = contestant
    ai.sleeping_arrangements = str2bool(form.sleeping_arrangements.data)
    si.contestant = contestant
    pi.contestant = contestant

    mi.contestant = contestant

    if new_dancer:
        db.session.add(contestant)
        si.set_status(NO_GDPR)
    db.session.commit()
    return contestant


def update_dancing_info(form, di_ballroom, di_latin):
    if di_ballroom.level == NO:
        di_ballroom.not_dancing(BALLROOM)
    else:
        di_ballroom.level = form.ballroom_level.data
        di_ballroom.role = form.ballroom_role.data
        di_ballroom.blind_date = str2bool(form.ballroom_blind_date.data)
        db.session.add(di_ballroom)
        db.session.flush()
        if not str2bool(form.ballroom_blind_date.data) and form.ballroom_partner.data is not None:
            di_ballroom.set_partner(form.ballroom_partner.data.contestant_id)
        else:
            di_ballroom.set_partner(None)
    di_latin.level = form.latin_level.data
    di_latin.role = form.latin_role.data
    di_latin.blind_date = str2bool(form.latin_blind_date.data)
    db.session.add(di_latin)
    db.session.flush()
    if not str2bool(form.latin_blind_date.data) and form.latin_partner.data is not None:
        di_latin.set_partner(form.latin_partner.data.contestant_id)
    else:
        di_latin.set_partner(None)


def submit_updated_dancing_info(form, contestant):
    di_ballroom = contestant.competition(BALLROOM)
    di_latin = contestant.competition(LATIN)
    ballroom_parner, latin_partner = di_ballroom.partner, di_latin.partner
    update_dancing_info(form, di_ballroom, di_latin)
    partner = DancingInfo.query.filter(DancingInfo.contestant_id == ballroom_parner).first()
    if partner is not None:
        if di_ballroom.role == partner.role:
            di_ballroom.set_partner(None)
    partner = DancingInfo.query.filter(DancingInfo.contestant_id == latin_partner).first()
    if partner is not None:
        if di_latin.role == partner.role:
            di_latin.set_partner(None)
    db.session.commit()
    if di_ballroom.partner != ballroom_parner:
        send_lost_partner_notification(di_ballroom.contestant_id, BALLROOM, partner_id=ballroom_parner)
    if di_latin.partner != latin_partner:
        send_lost_partner_notification(di_ballroom.contestant_id, LATIN, partner_id=latin_partner)
    return contestant.get_full_name()


def send_lost_partner_notification(changed_id, competition, partner_id):
    dancer = Contestant.query.filter(Contestant.contestant_id == changed_id).first()
    partner = Contestant.query.filter(Contestant.contestant_id == partner_id).first()
    teamcaptain = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                    User.team == dancer.contestant_info.team).first()
    if dancer.contestant_info.team == partner.contestant_info.team:
        teamcaptain = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                        User.team == dancer.contestant_info.team).first()
        text = f"The organization has made changes to the dancing information of {dancer.get_full_name()}, and due " \
               f"to that, {dancer.first_name} and {partner.get_full_name()} are no longer dancing together " \
               f"in {competition}."
        n = Notification(title=f"Changed {competition} information of {dancer.get_full_name()} and "
                               f"{partner.get_full_name()}", text=text, user=teamcaptain)
        n.send()
    else:
        text_dancer = f"The organization has made changes to the dancing information of {dancer.get_full_name()}, " \
                      f"and due to that, {dancer.first_name} and {partner.get_full_name()} " \
                      f"({partner.contestant_info.team}) are no longer dancing together in {competition}."
        n = Notification(title=f"Changed {competition} information of {dancer.get_full_name()}",
                         text=text_dancer, user=teamcaptain)
        n.send()
        teamcaptain_partner = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN],
                                                User.team == partner.contestant_info.team).first()
        text_partner = f"The organization has made changes to the dancing information of {dancer.get_full_name()} " \
                       f"({dancer.contestant_info.team}), and due to that, {dancer.first_name} and " \
                       f"{partner.get_full_name()} are no longer dancing together in {competition}."
        n = Notification(title=f"Changed {competition} information of {partner.get_full_name()}",
                         text=text_partner, user=teamcaptain_partner)
        n.send()


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
