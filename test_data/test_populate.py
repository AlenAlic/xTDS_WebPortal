from flask import g
from ntds_webportal import db
from ntds_webportal.models import Team, Contestant, ContestantInfo, DancingInfo, VolunteerInfo, AdditionalInfo, \
    StatusInfo, MerchandiseInfo, PaymentInfo, User, MerchandiseItem, MerchandiseItemVariant, MerchandisePurchase
from ntds_webportal.data import ACCESS, DANCER, SHIRT_SIZES, NO, ORGANIZER, TEAM_CAPTAIN
from ntds_webportal.functions import reset_tournament_state
from test_data.etds2018brno import etds2018brno, etds2018brno_configuration
from test_data.ntds2018enschede import ntds2018enschede, ntds2018enschede_configuration
from test_data.ntds2019nijmegen import ntds2019nijmegen, ntds2019nijmegen_configuration
import datetime

PAST_TOURNAMENTS = {
    "NTDS 2018 Enschede": ntds2018enschede_configuration,
    "ETDS 2018 Brno": etds2018brno_configuration,
    "NTDS 2019 Nijmengen": ntds2019nijmegen_configuration,
}


def populate_test_data(tournament=None):

    if tournament is None:
        return False

    if tournament not in PAST_TOURNAMENTS:
        return False
    test_contestants = []
    test_configuration = {}

    reset_tournament_state()
    g.ts.organizer_account_set = True
    g.ts.system_configured = True

    if tournament == "NTDS 2018 Enschede":
        test_contestants = ntds2018enschede
        test_configuration = ntds2018enschede_configuration
    if tournament == "ETDS 2018 Brno":
        test_contestants = etds2018brno
        test_configuration = etds2018brno_configuration
    if tournament == "NTDS 2019 Nijmengen":
        test_contestants = ntds2019nijmegen
        test_configuration = ntds2019nijmegen_configuration

    User.query.filter(User.access >= ACCESS[ORGANIZER], User.access < ACCESS[TEAM_CAPTAIN])\
        .update({User.is_active: True})

    g.sc.tournament = test_configuration["tournament"]
    g.sc.number_of_teamcaptains = test_configuration["number_of_teamcaptains"]

    g.sc.beginners_level = test_configuration["beginners_level"]
    g.sc.closed_level = test_configuration["closed_level"]
    g.sc.breitensport_obliged_blind_date = test_configuration["breitensport_obliged_blind_date"]
    g.sc.salsa_competition = test_configuration["salsa_competition"]
    g.sc.polka_competition = test_configuration["polka_competition"]

    g.sc.student_price = test_configuration["student_price"]
    g.sc.non_student_price = test_configuration["non_student_price"]
    g.sc.phd_student_category = test_configuration["phd_student_category"]
    g.sc.phd_student_price = test_configuration["phd_student_price"]

    g.sc.first_time_ask = test_configuration["first_time_ask"]
    g.sc.ask_adult = test_configuration["ask_adult"]
    g.sc.ask_diet_allergies = test_configuration["ask_diet_allergies"]
    g.sc.ask_volunteer = test_configuration["ask_volunteer"]
    g.sc.ask_first_aid = test_configuration["ask_first_aid"]
    g.sc.ask_emergency_response_officer = test_configuration["ask_emergency_response_officer"]
    g.sc.ask_adjudicator_highest_achieved_level = test_configuration["ask_adjudicator_highest_achieved_level"]
    g.sc.ask_adjudicator_certification = test_configuration["ask_adjudicator_certification"]

    for merchandise in test_configuration["merchandise"]:
        if merchandise["shirt"]:
            for variant in merchandise["variants"]:
                item = MerchandiseItem(description=f'{variant} {merchandise["description"]}',
                                       shirt=merchandise["shirt"], price=merchandise["price"])
                for size in SHIRT_SIZES:
                    MerchandiseItemVariant(merchandise_item=item, variant=size)
                db.session.add(item)
        else:
            item = MerchandiseItem(description=merchandise["description"],
                                   shirt=merchandise["shirt"], price=merchandise["price"])
            for variant in merchandise["variants"]:
                MerchandiseItemVariant(merchandise_item=item, variant=variant)
            db.session.add(item)

    g.sc.finances_full_refund = test_configuration["finances_full_refund"]
    g.sc.finances_partial_refund = test_configuration["finances_partial_refund"]
    g.sc.finances_partial_refund_percentage = test_configuration["finances_partial_refund_percentage"]

    now = datetime.datetime.now()
    now = datetime.datetime(year=now.year, month=now.month, day=now.day)
    refund_date = now + datetime.timedelta((2-now.weekday()) % 7)
    merchandise_date = refund_date + datetime.timedelta(days=8)
    tournament_start_date = merchandise_date + datetime.timedelta(days=8)
    g.sc.tournament_starting_date = int(tournament_start_date.timestamp())
    g.sc.finances_refund_date = int(refund_date.timestamp())
    g.sc.merchandise_closing_date = int(merchandise_date.timestamp())

    db.session.commit()

    for test_c in test_contestants:
        c = Contestant()
        c.contestant_id = test_c['contestant_id']
        c.first_name = test_c['first_name']
        if 'prefixes' in test_c:
            c.prefixes = test_c['prefixes']
        c.last_name = test_c['last_name']
        print('... Adding {}'.format(c.get_full_name()))
        c.email = test_c['email']
        db.session.add(c)
        c_info = ContestantInfo()
        c_info.number = test_c['number']
        c_info.team_captain = test_c['team_captain']
        c_info.student = test_c['student']
        c_info.first_time = test_c['first_time']
        c_info.diet_allergies = test_c['diet_allergies']
        c_info.team = db.session.query(Team).filter_by(city=test_c['team']).first()
        c_info.contestant = c
        for di in test_c['dancing_info']:
            d_info = DancingInfo()
            d_info.contestant = c
            d_info.competition = di['competition']
            d_info.level = di['level']
            d_info.role = di['role']
            d_info.blind_date = di['blind_date']
            d_info.partner = di['partner']
            db.session.add(d_info)
        v_info = VolunteerInfo()
        v_info.volunteer = test_c['volunteer']
        v_info.first_aid = test_c['first_aid']
        v_info.emergency_response_officer = test_c['emergency_response_officer']
        v_info.jury_ballroom = test_c['jury_ballroom']
        v_info.jury_latin = test_c['jury_latin']
        v_info.license_jury_ballroom = test_c['license_ballroom']
        v_info.license_jury_latin = test_c['license_latin']
        v_info.level_ballroom = test_c['ballroom_highest_level']
        v_info.level_latin = test_c['latin_highest_level']
        v_info.jury_salsa = test_c['jury_latin']
        v_info.jury_polka = test_c['jury_latin']
        v_info.contestant = c
        a_info = AdditionalInfo()
        a_info.sleeping_arrangements = test_c['sleeping_arrangements']
        a_info.contestant = c
        s_info = StatusInfo()
        s_info.guaranteed_entry = test_c['guaranteed_entry']
        s_info.contestant = c
        m_info = MerchandiseInfo()
        m_info.contestant = c
        if 't_shirt' in test_c['merchandise']:
            if test_c['merchandise']['t_shirt'] != NO:
                MerchandisePurchase(merchandise_info=m_info,
                                    merchandise_item_variant=MerchandiseItemVariant.query
                                    .filter(MerchandiseItemVariant.variant == test_c['merchandise']['t_shirt']).first())
        for p in test_c['merchandise']:
            variant = MerchandiseItemVariant.query.join(MerchandiseItem)\
                .filter(MerchandiseItemVariant.variant == test_c['merchandise'][p], MerchandiseItem.description == p)\
                .first()
            MerchandisePurchase(merchandise_info=m_info, merchandise_item_variant=variant)
        p_info = PaymentInfo()
        p_info.contestant = c
        dancer_account = User()
        dancer_account.team = db.session.query(Team).filter_by(city=test_c['team']).first()
        dancer_account.username = test_c['email']
        dancer_account.email = test_c['email']
        dancer_account.set_password('test')
        dancer_account.access = ACCESS[DANCER]
        dancer_account.is_active = True
        dancer_account.send_new_messages_email = False
        dancer_account.dancer = c
    db.session.commit()
    return True
