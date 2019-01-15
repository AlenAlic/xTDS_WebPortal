from flask import g
from ntds_webportal import db
from ntds_webportal.models import Team, Contestant, ContestantInfo, DancingInfo, VolunteerInfo, AdditionalInfo, \
    StatusInfo, MerchandiseInfo, PaymentInfo
from ntds_webportal.data import NTDS, ETDS


def populate_test_data(tournament=None):

    if tournament is None:
        return False

    past_tournaments = ["NTDS2018ENSCHEDE", "ETDS2018BRNO"]

    from instance.etds2018brno import etds2018brno
    from instance.ntds2018enschede import ntds2018enschede

    if tournament not in past_tournaments:
        return False
    test_contestants = []
    if tournament == "NTDS2018ENSCHEDE":
        test_contestants = ntds2018enschede

        g.sc.tournament = NTDS
        g.sc.number_of_teamcaptains = 2

        g.sc.beginners_level = True
        g.sc.closed_level = False
        g.sc.breitensport_obliged_blind_date = True
        g.sc.salsa_competition = False
        g.sc.polka_competition = False

        g.sc.student_price = 5800
        g.sc.non_student_price = 7300
        g.sc.phd_student_category = True
        g.sc.phd_student_price = 6300

        g.sc.first_time_ask = True
        g.sc.ask_diet_allergies = True
        g.sc.ask_volunteer = True
        g.sc.ask_first_aid = True
        g.sc.ask_emergency_response_officer = True
        g.sc.ask_adjudicator_highest_achieved_level = True
        g.sc.ask_adjudicator_certification = False

        g.sc.t_shirt_sold = False
        g.sc.t_shirt_price = 0
        g.sc.mug_sold = True
        g.sc.mug_price = 610
        g.sc.bag_sold = True
        g.sc.bag_price = 900

        g.sc.finances_full_refund = True
        g.sc.finances_partial_refund = False
        g.sc.finances_partial_refund_percentage = 0
    elif tournament == "ETDS2018BRNO":
        test_contestants = etds2018brno

        g.sc.tournament = ETDS
        g.sc.number_of_teamcaptains = 1

        g.sc.beginners_level = False
        g.sc.closed_level = True
        g.sc.breitensport_obliged_blind_date = False
        g.sc.salsa_competition = True
        g.sc.polka_competition = True

        g.sc.student_price = 8000
        g.sc.non_student_price = 9000
        g.sc.phd_student_category = False
        g.sc.phd_student_price = 0

        g.sc.first_time_ask = True
        g.sc.ask_diet_allergies = False
        g.sc.ask_volunteer = False
        g.sc.ask_first_aid = False
        g.sc.ask_emergency_response_officer = False
        g.sc.ask_adjudicator_highest_achieved_level = True
        g.sc.ask_adjudicator_certification = True

        g.sc.t_shirt_sold = True
        g.sc.t_shirt_price = 1500
        g.sc.mug_sold = False
        g.sc.mug_price = 0
        g.sc.bag_sold = False
        g.sc.bag_price = 0

        g.sc.finances_full_refund = False
        g.sc.finances_partial_refund = False
        g.sc.finances_partial_refund_percentage = 0

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
        m_info.t_shirt = test_c['t_shirt']
        m_info.contestant = c
        p_info = PaymentInfo()
        p_info.contestant = c
    db.session.commit()
    return True
