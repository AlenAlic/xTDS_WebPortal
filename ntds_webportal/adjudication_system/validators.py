# noinspection PyProtectedMember
from wtforms.validators import ValidationError
from ntds_webportal.models import Competition, CompetitionMode, Couple, Adjudicator
from ntds_webportal.data import OPPOSITE_ROLES


CANNOT_ADD_TO_COMPETITION = 'Cannot add this couple to the competition {comp}, {d} is already dancing in ' \
                            'that competition.'
CANNOT_SAVE_COMPETITION = "Cannot save current couples, {d} ({role}) is more than once in the competition."


class UniqueDancer(object):
    """Checks if a dancer is already in the selected competitions."""
    def __call__(self, form, field):
        comps = Competition.query.filter(Competition.competition_id.in_(form.competitions.data)).all()
        for comp in [c for c in comps]:
            if form.lead.data in [c.lead for c in comp.couples]:
                raise ValidationError(field.gettext(CANNOT_ADD_TO_COMPETITION.format(comp=comp, d=form.lead.data)))
            if form.follow.data in [c.follow for c in comp.couples]:
                raise ValidationError(field.gettext(CANNOT_ADD_TO_COMPETITION.format(comp=comp, d=form.follow.data)))


class UniqueDancerEdit(object):
    """Checks if a dancer is already in the selected competitions."""
    def __call__(self, form, field):
        comps = Competition.query.filter(Competition.competition_id.in_(form.competitions.data)).all()
        for comp in [c for c in comps]:
            if form.lead.data in [c.lead for c in comp.couples if c != form.couple]:
                raise ValidationError(field.gettext(CANNOT_ADD_TO_COMPETITION.format(comp=comp, d=form.lead.data)))
            if form.follow.data in [c.follow for c in comp.couples if c != form.couple]:
                raise ValidationError(field.gettext(CANNOT_ADD_TO_COMPETITION.format(comp=comp, d=form.follow.data)))


class EqualNumberLeadsFollows(object):
    """"Checks if there are an equal amount of leads and follows in the competition"""
    def __call__(self, form, field):
        if form.competition.mode != CompetitionMode.single_partner:
            if len(form.competition.leads) != len(form.competition.follows):
                raise ValidationError(field.gettext(f"Cannot create first round, there "
                                                    f"are {len(form.competition.leads)} Leads "
                                                    f"and {len(form.competition.follows)} Follows assigned to this"
                                                    f" competition."))


class UniqueDancerCompetition(object):
    """Checks if there are no double dancers in the competition."""
    def __call__(self, form, field):
        couples = Couple.query.filter(Couple.couple_id.in_(form.competition_couples.data))
        leads = [c.lead for c in couples]
        follows = [c.follow for c in couples]
        for dancer in leads:
            if leads.count(dancer) > 1:
                raise ValidationError(field.gettext(CANNOT_SAVE_COMPETITION.format(d=dancer, role="lead")))
        for dancer in follows:
            if follows.count(dancer) > 1:
                raise ValidationError(field.gettext(CANNOT_SAVE_COMPETITION.format(d=dancer, role="follow")))


class UniqueTag(object):
    """Checks if the adjudicator tag is unique."""
    def __call__(self, form, field):
        tags = [a.tag for a in Adjudicator.query.all()]


class UniqueCompetitionDancer(object):
    """Checks if a dancer is already in the selected competitions."""
    def __call__(self, form, field):
        comps = Competition.query.filter(Competition.competition_id.in_(form.competitions.data)).all()
        for comp in [c for c in comps]:
            if form.dancer.number in [d.number for d in comp.dancers()]:
                raise ValidationError(field.gettext(f"Cannot add {form.dancer} to {comp}. He/She is already dancing "
                                                    f"there as a {OPPOSITE_ROLES[form.dancer.role]}."))
