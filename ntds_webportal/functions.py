from ntds_webportal import db
from ntds_webportal.models import Team, Contestant, ContestantInfo, DancingInfo, VolunteerInfo, AdditionalInfo, \
    StatusInfo, MerchandiseInfo, Merchandise
import ntds_webportal.data as data
from ntds_webportal.data import *


def str2bool(v):
    return v in (str(True))


def get_dancing_categories(dancing_info):
    return {cat: DancingInfo(competition=cat) for cat in ALL_COMPETITIONS} if dancing_info is None \
        else {di.competition: di for di in dancing_info}


def get_discipline(dancer, discipline):
    for di in dancer.dancing_info:
        if di.competition == discipline:
            return di
    return None


def get_partners_ids(dancer):
    return [cat.partner for cat in dancer.dancing_info if cat.partner is not None]


def has_partners(dancer):
    return get_partners_ids(dancer) != []


def uniquify(seq):
    s = set(seq)
    s = list(s)
    s.sort()
    return s if len(seq) > 0 else []


def check_combination(dancer, combination):
    dc = []
    for di in dancer.dancing_info:
        if di.level != NO:
            dc.extend([di.competition, di.level, di.role])
    return dc == combination


def get_combinations_list(s):
    s = s.replace(' / ', ', ')
    return s.split(', ')


def get_total_dancer_price_list(dancer):
    number_of_stickers = sum([m.quantity for m in
                              MerchandiseInfo.query.filter_by(contestant_id=dancer.contestant_id).all()])
    student = dancer.contestant_info[0].student
    t_shirt = dancer.additional_info[0].t_shirt
    price = PRICES['student'][student] + PRICES['t-shirt'][t_shirt] + PRICES['stickers'] * number_of_stickers
    student_string = {True: 'Student', False: 'Non-student'}
    description = f"ETDS Brno 2018 - {student_string[student]} entry fee"
    if t_shirt != NO:
        description += " + t-shirt"
    if number_of_stickers > 0:
        description += f" + {number_of_stickers} stickers"
    paid_string = {True: "Yes", False: "No"}
    return [dancer.get_full_name(), price/100, description, paid_string[dancer.status_info[0].paid]]


def contestant_validate_dancing(form):
    try:
        form.first_name.data = form.first_name.data.capitalize()
        form.last_name.data = form.last_name.data.capitalize()
    except AttributeError:
        pass
    if form.ballroom_partner.data is not None:
        if form.ballroom_level.data in BLIND_DATE_LEVELS:
            form.ballroom_partner.data = 'must_blind_date'
        else:
            # noinspection PyUnresolvedReferences
            dancing_partner = db.session.query(Contestant) \
                .filter(Contestant.contestant_id == form.ballroom_partner.data.contestant_id).first()
            dancing_categories = get_dancing_categories(dancing_partner.dancing_info)
            if form.ballroom_level.data != dancing_categories[BALLROOM].level:
                if dancing_categories[BALLROOM].level is None:
                    form.ballroom_partner.data = 'diff_levels_no_level'
                    form.ballroom_level.data = 'diff_levels_no_level'
                elif form.ballroom_level.data != CHOOSE:
                    form.ballroom_partner.data = 'diff_levels'
                    form.ballroom_level.data = 'diff_levels'
            if form.ballroom_role.data == dancing_categories[BALLROOM].role:
                if form.ballroom_role.data == LEAD:
                    form.ballroom_partner.data = 'same_role_lead'
                    form.ballroom_role.data = 'same_role_lead'
                elif form.ballroom_role.data == FOLLOW:
                    form.ballroom_partner.data = 'same_role_follow'
                    form.ballroom_role.data = 'same_role_follow'
    if form.latin_partner.data is not None:
        if form.latin_level.data in BLIND_DATE_LEVELS:
            form.latin_partner.data = 'must_blind_date'
        else:
            # noinspection PyUnresolvedReferences
            dancing_partner = db.session.query(Contestant) \
                .filter(Contestant.contestant_id == form.latin_partner.data.contestant_id).first()
            dancing_categories = get_dancing_categories(dancing_partner.dancing_info)
            if form.latin_level.data != dancing_categories[LATIN].level:
                if dancing_categories[LATIN].level is None:
                    form.latin_partner.data = 'diff_levels_no_level'
                    form.latin_level.data = 'diff_levels_no_level'
                elif form.latin_level.data != CHOOSE:
                    form.latin_partner.data = 'diff_levels'
                    form.latin_level.data = 'diff_levels'
            if form.latin_role.data == dancing_categories[LATIN].role:
                if form.latin_role.data == LEAD:
                    form.latin_partner.data = 'same_role_lead'
                    form.latin_role.data = 'same_role_lead'
                elif form.latin_role.data == FOLLOW:
                    form.latin_partner.data = 'same_role_follow'
                    form.latin_role.data = 'same_role_follow'
    form.volunteer.data = NO
    form.first_aid.data = NO
    return form


def submit_contestant(f, contestant=None):
    new_dancer = True
    merchandises = Merchandise.query.all()
    if contestant is None:
        contestant = Contestant()
        ci = ContestantInfo()
        dancing_categories = get_dancing_categories(None)
        vi = VolunteerInfo()
        ai = AdditionalInfo()
        si = StatusInfo()
        contestant.first_name = f.first_name.data
        contestant.prefixes = f.prefixes.data if f.prefixes.data != '' else None
        contestant.last_name = f.last_name.data
        ci.number = f.number.data
        ci.team = db.session.query(Team).filter_by(name=f.team.data).first()
    else:
        ci = contestant.contestant_info[0]
        di = contestant.dancing_info
        vi = contestant.volunteer_info[0]
        ai = contestant.additional_info[0]
        si = contestant.status_info[0]
        mi = contestant.merchandise_info
        if len(mi) > 0:
            for m in mi:
                ref_merch = [merch for merch in merchandises if merch.merchandise_id == m.product_id][0]
                m.quantity = getattr(f, ref_merch.product_name).data
        else:
            for key, value in MERCHANDISE.items():
                mi = MerchandiseInfo()
                mi.contestant = contestant
                mi.product_id = [merch for merch in merchandises if merch.product_name == key][0].merchandise_id
                mi.quantity = int(getattr(f, key).data)
                db.session.add(mi)
        dancing_categories = get_dancing_categories(di)
        new_dancer = False
    contestant.email = f.email.data
    ci.contestant = contestant
    ci.student = str2bool(f.student.data)
    ci.first_time = str2bool(f.first_time.data)
    ci.diet_allergies = f.diet_allergies.data
    dancing_categories[BALLROOM].contestant = contestant
    dancing_categories[LATIN].contestant = contestant
    if f.ballroom_level.data == NO:
        dancing_categories[BALLROOM].not_dancing(BALLROOM)
        db.session.add(dancing_categories[BALLROOM])
    else:
        dancing_categories[BALLROOM].level = f.ballroom_level.data
        dancing_categories[BALLROOM].role = f.ballroom_role.data
        dancing_categories[BALLROOM].blind_date = f.ballroom_blind_date.data
        db.session.add(dancing_categories[BALLROOM])
        db.session.flush()
        if f.ballroom_partner.data is not None:
            dancing_categories[BALLROOM].set_partner(f.ballroom_partner.data.contestant_id)
        else:
            dancing_categories[BALLROOM].set_partner(None)
    if f.latin_level.data == NO:
        dancing_categories[LATIN].not_dancing(LATIN)
        db.session.add(dancing_categories[LATIN])
    else:
        dancing_categories[LATIN].level = f.latin_level.data
        dancing_categories[LATIN].role = f.latin_role.data
        dancing_categories[LATIN].blind_date = f.latin_blind_date.data
        db.session.add(dancing_categories[LATIN])
        db.session.flush()
        if f.latin_partner.data is not None:
            dancing_categories[LATIN].set_partner(f.latin_partner.data.contestant_id)
        else:
            dancing_categories[LATIN].set_partner(None)
    vi.contestant = contestant
    vi.volunteer = f.volunteer.data
    vi.first_aid = f.first_aid.data
    vi.jury_ballroom = f.jury_ballroom.data
    vi.jury_latin = f.jury_latin.data
    vi.license_jury_ballroom = f.license_jury_ballroom.data
    vi.license_jury_latin = f.license_jury_latin.data
    vi.jury_salsa = f.jury_salsa.data
    vi.jury_polka = f.jury_polka.data
    ai.contestant = contestant
    ai.sleeping_arrangements = str2bool(f.sleeping_arrangements.data)
    ai.t_shirt = f.t_shirt.data
    si.contestant = contestant
    if new_dancer:
        db.session.add(contestant)
        for key, value in MERCHANDISE.items():
            mi = MerchandiseInfo()
            mi.contestant = contestant
            mi.product_id = [merch for merch in merchandises if merch.product_name == key][0].merchandise_id
            mi.quantity = int(getattr(f, key).data)
            db.session.add(mi)
    db.session.commit()
    return contestant.get_full_name()
