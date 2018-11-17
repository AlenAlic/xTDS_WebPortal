from ntds_webportal import db
from ntds_webportal.models import SystemConfiguration, Contestant, ContestantInfo, StatusInfo, DancingInfo
from ntds_webportal.data import *
from sqlalchemy import or_, and_


class TeamPossiblePartners:

    def __init__(self, team_captain, status=REGISTERED, other_teams=False, include_external_partners_of=None,
                 include_gdpr=False):
        self.team = team_captain.team
        self.status = status
        self.other_teams = other_teams
        self.include_external_partners_of = include_external_partners_of
        self.include_gdpr = include_gdpr

    def get_dancing_info_list(self, competition, level, role):
        dancers = DancingInfo.query\
            .join(StatusInfo, DancingInfo.contestant_id == StatusInfo.contestant_id)\
            .join(ContestantInfo, DancingInfo.contestant_id == ContestantInfo.contestant_id) \
            .join(Contestant, DancingInfo.contestant_id == Contestant.contestant_id) \
            .order_by(Contestant.first_name)
        if self.include_gdpr:
            dancers = dancers.filter(or_(StatusInfo.status == self.status, StatusInfo.status == NO_GDPR))
        else:
            dancers = dancers.filter(StatusInfo.status == self.status)
        if not self.other_teams and self.include_external_partners_of is not None:
            external_partners = dancers.filter(DancingInfo.competition == competition,
                                               DancingInfo.level == level, DancingInfo.role == role,
                                               DancingInfo.partner == self.include_external_partners_of.contestant_id)\
                .filter(ContestantInfo.team != self.team).all()
        else:
            external_partners = []
        dancers = dancers.filter(DancingInfo.competition == competition,
                                 DancingInfo.level == level, DancingInfo.role == role,
                                 DancingInfo.blind_date.is_(False), DancingInfo.partner.is_(None))
        if self.other_teams:
            dancers = dancers.filter(ContestantInfo.team != self.team).all()
        else:
            dancers = dancers.filter(ContestantInfo.team == self.team).all()
        return dancers + external_partners

    def ballroom_beginners_leads(self):
        return self.get_dancing_info_list(BALLROOM, BEGINNERS, LEAD)

    def ballroom_beginners_follows(self):
        return self.get_dancing_info_list(BALLROOM, BEGINNERS, FOLLOW)

    def latin_beginners_leads(self):
        return self.get_dancing_info_list(LATIN, BEGINNERS, LEAD)

    def latin_beginners_follows(self):
        return self.get_dancing_info_list(LATIN, BEGINNERS, FOLLOW)

    def ballroom_breitensport_leads(self):
        return self.get_dancing_info_list(BALLROOM, BREITENSPORT, LEAD)

    def ballroom_breitensport_follows(self):
        return self.get_dancing_info_list(BALLROOM, BREITENSPORT, FOLLOW)

    def latin_breitensport_leads(self):
        return self.get_dancing_info_list(LATIN, BREITENSPORT, LEAD)

    def latin_breitensport_follows(self):
        return self.get_dancing_info_list(LATIN, BREITENSPORT, FOLLOW)
    
    @staticmethod
    def choices(dancers, extra_dancers=None):
        if extra_dancers is not None:
            dancers += extra_dancers
        dancers = [(str(dancer.contestant_id), dancer.contestant.get_full_name(),
                    dancer.contestant.contestant_info[0].team.name) for dancer in dancers]
        if extra_dancers is not None:
            dancers.sort(key=lambda dancer: dancer[1])
        return dancers

    def possible_partners(self):
        return {BALLROOM: {BEGINNERS: {LEAD: self.choices(self.ballroom_beginners_follows()),
                                       FOLLOW: self.choices(self.ballroom_beginners_leads()),
                                       BOTH: self.choices(self.ballroom_beginners_leads(),
                                                          self.ballroom_beginners_follows())
                                       },
                           BREITENSPORT: {LEAD: self.choices(self.ballroom_breitensport_follows()),
                                          FOLLOW: self.choices(self.ballroom_breitensport_leads()),
                                          BOTH: self.choices(self.ballroom_breitensport_leads(),
                                                             self.ballroom_breitensport_follows())
                                          }},
                LATIN: {BEGINNERS: {LEAD: self.choices(self.latin_beginners_follows()),
                                    FOLLOW: self.choices(self.latin_beginners_leads()),
                                    BOTH: self.choices(self.latin_beginners_leads(),
                                                       self.latin_beginners_follows())
                                    },
                        BREITENSPORT: {LEAD: self.choices(self.latin_breitensport_follows()),
                                       FOLLOW: self.choices(self.latin_breitensport_leads()),
                                       BOTH: self.choices(self.latin_breitensport_leads(),
                                                          self.latin_breitensport_follows())
                                       }}
                }


class TeamFinancialOverview:

    def __init__(self, team_captain):
        self.config = SystemConfiguration.query.first()
        self.team_captain = team_captain
        self.dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
            .filter(ContestantInfo.team == team_captain.team, StatusInfo.payment_required.is_(True)) \
            .order_by(ContestantInfo.number).all()

    def student_prices(self):
        student_prices = {STUDENT: self.config.student_price, NON_STUDENT: self.config.non_student_price,
                          PHD_STUDENT: self.config.phd_student_price}
        return student_prices

    def prices(self):
        prices = self.student_prices()
        prices.update(dict({NO: 0}, **{k: self.config.t_shirt_price for k, v in SHIRT_SIZES.items()}))
        prices.update({MUG: self.config.mug_price, BAG: self.config.bag_price})
        return prices

    def get_dancers(self, price_category, paid):
        prices = self.student_prices()
        dancers = [prices[dancer.contestant_info[0].student] for dancer in self.dancers if
                   dancer.contestant_info[0].student == price_category and dancer.payment_info[0].entry_paid is paid]
        return dancers

    def get_students(self, paid):
        students = self.get_dancers(STUDENT, paid)
        return len(students), sum(students)
    
    def get_non_students(self, paid):
        students = self.get_dancers(NON_STUDENT, paid)
        return len(students), sum(students)
    
    def get_phd_students(self, paid):
        students = self.get_dancers(PHD_STUDENT, paid)
        return len(students), sum(students)

    def get_t_shirts(self, paid):
        t_shirts = [self.config.t_shirt_price for dancer in self.dancers if dancer.merchandise_info[0].t_shirt != NO
                    and dancer.merchandise_info[0].t_shirt_paid is paid]
        return len(t_shirts), sum(t_shirts)
    
    def get_mugs(self, paid):
        mugs = [self.config.mug_price for dancer in self.dancers if dancer.merchandise_info[0].mug
                and dancer.merchandise_info[0].mug_paid is paid]
        return len(mugs), sum(mugs)
    
    def get_bags(self, paid):
        bags = [self.config.bag_price for dancer in self.dancers if dancer.merchandise_info[0].bag
                and dancer.merchandise_info[0].bag_paid is paid]
        return len(bags), sum(bags)

    def get_total(self, paid):
        ns, ps = self.get_students(paid)
        nns, pns = self.get_non_students(paid)
        nps, pps = self.get_phd_students(paid)
        nts, pts = self.get_t_shirts(paid)
        return ns + nns + nps + nts, ps + pns + pps + pts
    
    def get_merchandise(self, paid):
        nts, pts = self.get_t_shirts(paid)
        nms, pms = self.get_mugs(paid)
        nbs, pbs = self.get_bags(paid)
        return nts + nms + nbs, pts + pms + pbs

    def finances_overview(self):
        number_students_paid, students_paid = self.get_students(True)
        number_students_unpaid, students_unpaid,  = self.get_students(False)
        number_non_students_paid, non_students_paid = self.get_non_students(True)
        number_non_students_unpaid, non_students_unpaid = self.get_non_students(False)
        number_phd_students_paid, phd_students_paid = self.get_phd_students(True)
        number_phd_students_unpaid, phd_students_unpaid = self.get_phd_students(False)
        number_shirts_paid, shirts_paid = self.get_t_shirts(True)
        number_shirts_unpaid, shirts_unpaid = self.get_t_shirts(False)
        number_mugs_paid, mugs_paid = self.get_mugs(True)
        number_mugs_unpaid, mugs_unpaid = self.get_mugs(False)
        number_bags_paid, bags_paid = self.get_bags(True)
        number_bags_unpaid, bags_unpaid = self.get_bags(False)
        number_merchandise_paid, merchandise_paid = self.get_merchandise(True)
        number_merchandise_unpaid, merchandise_unpaid = self.get_merchandise(False)
        result = self.prices()
        result\
            .update({'number_of_students_unpaid': number_students_unpaid,
                     'price_students_unpaid': students_unpaid,
                     'number_of_students_paid': number_students_paid,
                     'price_students_paid': students_paid,
                     'number_of_students': number_students_unpaid + number_students_paid,
                     'price_students': students_unpaid + students_paid,

                     'number_of_non_students_unpaid': number_non_students_unpaid,
                     'price_non_students_unpaid': non_students_unpaid,
                     'number_of_non_students_paid': number_non_students_paid,
                     'price_non_students_paid': non_students_paid,
                     'number_of_non_students': number_non_students_unpaid + number_non_students_paid,
                     'price_non_students': non_students_unpaid + non_students_paid,
                     
                     'number_of_phd_students_unpaid': number_phd_students_unpaid,
                     'price_phd_students_unpaid': phd_students_unpaid,
                     'number_of_phd_students_paid': number_phd_students_paid,
                     'price_phd_students_paid': phd_students_paid,
                     'number_of_phd_students': number_phd_students_unpaid + number_phd_students_paid,
                     'price_phd_students': phd_students_unpaid + phd_students_paid,

                     'number_of_t-shirts_unpaid': number_shirts_unpaid,
                     'price_t-shirts_unpaid': shirts_unpaid,
                     'number_of_t-shirts_paid': number_shirts_paid,
                     'price_t-shirts_paid': shirts_paid,
                     'number_of_t-shirts': number_shirts_unpaid + number_shirts_paid,
                     'price_t-shirts': shirts_unpaid + shirts_paid,

                     'number_of_mugs_unpaid': number_mugs_unpaid,
                     'price_mugs_unpaid': mugs_unpaid,
                     'number_of_mugs_paid': number_mugs_paid,
                     'price_mugs_paid': mugs_paid,
                     'number_of_mugs': number_mugs_unpaid + number_mugs_paid,
                     'price_mugs': mugs_unpaid + mugs_paid,

                     'number_of_bags_unpaid': number_bags_unpaid,
                     'price_bags_unpaid': bags_unpaid,
                     'number_of_bags_paid': number_bags_paid,
                     'price_bags_paid': bags_paid,
                     'number_of_bags': number_bags_unpaid + number_bags_paid,
                     'price_bags': bags_unpaid + bags_paid,

                     'number_of_merchandise_unpaid': number_merchandise_unpaid,
                     'price_merchandise_unpaid': merchandise_unpaid,
                     'number_of_merchandise_paid': number_merchandise_paid,
                     'price_merchandise_paid': merchandise_paid,
                     'number_of_merchandise': number_merchandise_unpaid + number_merchandise_paid,
                     'price_merchandise': merchandise_unpaid + merchandise_paid,

                     'number_of_dancers_unpaid': (number_students_unpaid + number_non_students_unpaid +
                                                  number_phd_students_unpaid),
                     'price_dancers_unpaid': students_unpaid + non_students_unpaid + phd_students_unpaid,
                     'number_of_dancers_paid': (number_students_paid + number_non_students_paid +
                                                number_phd_students_paid),
                     'price_dancers_paid': students_paid + non_students_paid + phd_students_paid,
                     'number_of_dancers': (number_students_unpaid + number_students_paid +
                                           number_non_students_unpaid + number_non_students_paid +
                                           number_phd_students_unpaid + number_phd_students_paid),
                     'price_dancers': (students_unpaid + students_paid +
                                       non_students_unpaid + non_students_paid +
                                       phd_students_unpaid + phd_students_paid),

                     'total_number_of_payments_unpaid': (number_students_unpaid + number_non_students_unpaid +
                                                         number_phd_students_unpaid),
                     'price_total_unpaid': (students_unpaid + non_students_unpaid + phd_students_unpaid +
                                            merchandise_unpaid),
                     'total_number_of_payments_paid': (number_students_paid + number_non_students_paid +
                                                       number_phd_students_paid),
                     'price_total_paid': students_paid + non_students_paid + phd_students_paid + merchandise_paid,
                     'total_number_of_payments': (number_students_unpaid + number_non_students_unpaid +
                                                  number_phd_students_unpaid + number_students_paid +
                                                  number_non_students_paid + number_phd_students_paid),
                     'price_total': (students_unpaid + students_paid +
                                     non_students_paid + non_students_unpaid +
                                     phd_students_unpaid + phd_students_paid +
                                     merchandise_unpaid + merchandise_paid)
                     })
        return result
