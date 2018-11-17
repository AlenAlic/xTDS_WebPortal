from flask import request
from flask_login import current_user
from ntds_webportal import db
from ntds_webportal.models import Team, Contestant, ContestantInfo, DancingInfo, VolunteerInfo, AdditionalInfo, \
    StatusInfo, MerchandiseInfo, Merchandise, User, Notification
from ntds_webportal.data import *
from sqlalchemy import and_, or_


def str2bool(v):
    return v in (str(True))


def get_dancing_categories(dancing_info):
    if dancing_info is None:
        return {cat: DancingInfo(competition=cat) for cat in ALL_COMPETITIONS}
    else:
        return {di.competition: di for di in dancing_info}


def notify_teamcaptains_couple_created(lead, follow, competition):
    teamcaptain_lead = User.query.filter(User.is_active, User.access == ACCESS['team_captain'],
                                         User.team == lead.contestant_info[0].team).first()
    text = "{dancer} has found a partner. He/She has signed up for {comp} with {partner} from team {team}."
    n = Notification(title=f"{lead} found a dancing partner for {competition}",
                     text=text.format(dancer=lead.get_full_name(), comp=competition,
                                      partner=follow.get_full_name(), team=follow.contestant_info[0].team.name),
                     user=teamcaptain_lead)
    db.session.add(n)
    teamcaptain_follow = User.query.filter(User.is_active, User.access == ACCESS['team_captain'],
                                           User.team == follow.contestant_info[0].team).first()
    n2 = Notification(title=f"{follow} found a dancing partner for {competition}",
                      text=text.format(dancer=follow.get_full_name(), comp=competition,
                                       partner=lead.get_full_name(), team=lead.contestant_info[0].team.name),
                      user=teamcaptain_follow)
    db.session.add(n2)
    db.session.commit()


def notify_teamcaptains_broken_up_couple(lead, follow, competition):
    teamcaptain_lead = User.query.filter(User.is_active, User.access == ACCESS['team_captain'],
                                         User.team == lead.contestant_info[0].team).first()
    text = "{dancer} no longer has a partner in {comp}."
    n = Notification(title=f"{lead.get_full_name()} no longer has a partner for {competition}",
                     text=text.format(dancer=lead.get_full_name(), comp=competition), user=teamcaptain_lead)
    db.session.add(n)
    teamcaptain_follow = User.query.filter(User.is_active, User.access == ACCESS['team_captain'],
                                           User.team == follow.contestant_info[0].team).first()
    n2 = Notification(title=f"{follow.get_full_name()} no longer has a partner for {competition}",
                      text=text.format(dancer=follow.get_full_name(), comp=competition), user=teamcaptain_follow)
    db.session.add(n2)
    db.session.commit()


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
    merchandises = Merchandise.query.all()
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
        contestant.first_name = form.first_name.data
        contestant.prefixes = form.prefixes.data if form.prefixes.data.replace(' ', '') != '' else None
        contestant.last_name = form.last_name.data
        ci.number = form.number.data
        ci.team = form.team.data
    else:
        ci = contestant.contestant_info[0]
        vi = contestant.volunteer_info[0]
        ai = contestant.additional_info[0]
        si = contestant.status_info[0]
        mi = contestant.merchandise_info
        if len(mi) > 0:
            for m in mi:
                ref_merch = [merch for merch in merchandises if merch.merchandise_id == m.product_id][0]
                m.quantity = getattr(form, ref_merch.product_name).data
        else:
            for key, value in MERCHANDISE.items():
                mi = MerchandiseInfo()
                mi.contestant = contestant
                mi.product_id = [merch for merch in merchandises if merch.product_name == key][0].merchandise_id
                mi.quantity = int(getattr(form, key).data)
                db.session.add(mi)
        dancing_categories = get_dancing_categories(di)
        new_dancer = False
    contestant.email = form.email.data
    ci.contestant = contestant
    ci.student = str2bool(form.student.data)
    ci.first_time = str2bool(form.first_time.data)
    ci.diet_allergies = form.diet_allergies.data

    di_ballroom.contestant = contestant
    di_latin.contestant = contestant
    update_dancing_info(form, di_ballroom, di_latin)

    vi.contestant = contestant
    vi.volunteer = form.volunteer.data
    vi.first_aid = form.first_aid.data
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
    ai.t_shirt = form.t_shirt.data
    si.contestant = contestant
    if new_dancer:
        db.session.add(contestant)
        for key, value in MERCHANDISE.items():
            mi = MerchandiseInfo()
            mi.contestant = contestant
            mi.product_id = [merch for merch in merchandises if merch.product_name == key][0].merchandise_id
            mi.quantity = int(getattr(form, key).data)
            db.session.add(mi)
    db.session.commit()
    return contestant.get_full_name()


def update_dancing_info(form, dancing_categories):
    if form.ballroom_level.data == NO:
        dancing_categories[BALLROOM].not_dancing(BALLROOM)
        db.session.add(dancing_categories[BALLROOM])
    else:
        dancing_categories[BALLROOM].level = form.ballroom_level.data
        dancing_categories[BALLROOM].role = form.ballroom_role.data
        dancing_categories[BALLROOM].blind_date = form.ballroom_blind_date.data
        db.session.add(dancing_categories[BALLROOM])
        db.session.flush()
        if form.ballroom_level.data not in BLIND_DATE_LEVELS and form.ballroom_partner.data is not None:
            dancing_categories[BALLROOM].set_partner(form.ballroom_partner.data.contestant_id)
        else:
            dancing_categories[BALLROOM].set_partner(None)
    if form.latin_level.data == NO:
        dancing_categories[LATIN].not_dancing(LATIN)
        db.session.add(dancing_categories[LATIN])
    else:
        dancing_categories[LATIN].level = form.latin_level.data
        dancing_categories[LATIN].role = form.latin_role.data
        dancing_categories[LATIN].blind_date = form.latin_blind_date.data
        db.session.add(dancing_categories[LATIN])
        db.session.flush()
        if form.latin_level.data not in BLIND_DATE_LEVELS and form.latin_partner.data is not None:
            dancing_categories[LATIN].set_partner(form.latin_partner.data.contestant_id)
        else:
            dancing_categories[LATIN].set_partner(None)


def submit_updated_dancing_info(form, contestant):
    di_ballroom = contestant.competition(BALLROOM)
    di_latin = contestant.competition(LATIN)
    update_dancing_info(form, di_ballroom, di_latin)
    db.session.commit()
    return contestant.get_full_name()
