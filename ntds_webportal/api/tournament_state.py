from flask import jsonify, g
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import requires_access_level, User, Contestant, ContestantInfo
from ntds_webportal.api import bp
from ntds_webportal.organizer.email import send_raffle_completed_email
from ntds_webportal.data import *


@bp.route('/tournament_state/raffle_completed_message_sent/send_generic_email/', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def tournament_state_raffle_completed_message_sent_send_generic_email():
    if not g.ts.raffle_completed_message_sent:
        g.ts.raffle_completed_message_sent = True
        db.session.commit()
        teamcaptains = User.query.filter(User.is_active, User.access == ACCESS[TEAM_CAPTAIN]).all()
        for tc in teamcaptains:
            dancers = Contestant.query.join(ContestantInfo).filter(ContestantInfo.team == tc.team).all()
            if len(dancers) > 0:
                send_raffle_completed_email(tc.email)
    return jsonify(g.ts.raffle_completed_message_sent)


@bp.route('/tournament_state/raffle_completed_message_sent/send_own_email/', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def tournament_state_raffle_completed_message_sent_send_own_email():
    if not g.ts.raffle_completed_message_sent:
        g.ts.raffle_completed_message_sent = True
        db.session.commit()
    return jsonify(g.ts.raffle_completed_message_sent)
