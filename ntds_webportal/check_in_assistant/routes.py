from flask import render_template, g, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.check_in_assistant import bp
from ntds_webportal.models import requires_access_level, requires_tournament_state, Team, Contestant, ContestantInfo, \
    StatusInfo, User
from ntds_webportal.data import *
from ntds_webportal.functions import active_teams
from ntds_webportal.helper_classes import TeamFinancialOverview


@bp.route('/tournament_check_in', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def tournament_check_in():
    teams = active_teams()
    return render_template('check_in_assistant/tournament_check_in.html', teams=teams)


@bp.route('/check_in_teams', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def check_in_teams():
    return jsonify([{'team_id': team.team_id, 'name': team.name} for team in active_teams()])


@bp.route('/finances_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def finances_overview():
    team_id = request.args.get('team_id', 0, int)
    all_teams = Team.query.filter(Team.name != TEAM_SUPER_VOLUNTEER, Team.name != TEAM_ORGANIZATION)
    if g.sc.tournament == NTDS:
        all_teams = all_teams.filter(Team.country == NETHERLANDS).all()
    else:
        all_teams = all_teams.all()
    all_teams = [t for t in all_teams if t.is_active()]
    team = None
    if team_id in [t.team_id for t in all_teams]:
        team = Team.query.get(team_id)
    elif len(all_teams) > 0:
        team = all_teams[0]
        return redirect(url_for('check_in_assistant.finances_overview', team_id=team.team_id))
    if team is not None:
        confirmed_dancers = db.session.query(Contestant).join(ContestantInfo, StatusInfo) \
            .filter(StatusInfo.payment_required.is_(True), StatusInfo.status == CONFIRMED, ContestantInfo.team == team)\
            .order_by(Contestant.first_name).all()
        cancelled_dancers = db.session.query(Contestant).join(ContestantInfo, StatusInfo) \
            .filter(StatusInfo.payment_required.is_(True), StatusInfo.status == CANCELLED, ContestantInfo.team == team)\
            .order_by(Contestant.first_name).all()
        finances = TeamFinancialOverview(User.query.filter(User.team == team, User.access == ACCESS[TEAM_CAPTAIN])
                                         .first()).finances_overview()
        refund_dancers = []
        if g.sc.finances_full_refund:
            refund_dancers = [d for d in cancelled_dancers if d.payment_info.full_refund]
        if g.sc.finances_partial_refund:
            refund_dancers = [d for d in cancelled_dancers if d.payment_info.partial_refund]
        return render_template('check_in_assistant/finances_overview.html', all_teams=all_teams,
                               team=team, finances=finances, confirmed_dancers=confirmed_dancers,
                               cancelled_dancers=cancelled_dancers, refund_dancers=refund_dancers)
    else:
        flash('Team not found.')
        return redirect(url_for('main.dashboard'))
