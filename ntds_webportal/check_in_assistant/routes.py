from flask import render_template, flash, redirect, url_for, Markup
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.check_in_assistant import bp
from ntds_webportal.models import requires_access_level, requires_tournament_state, Contestant, ContestantInfo, User, \
    StatusInfo
from ntds_webportal.helper_classes import TeamFinancialOverview
from ntds_webportal.data import *
from ntds_webportal.functions import active_teams
from ntds_webportal.api.teams import team_confirmed_dancers


@bp.route('/tournament_check_in', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def tournament_check_in():
    teams = active_teams()
    teams = [{'team_id': team.team_id, 'name': team.name,
              'dancers': team_confirmed_dancers(team.team_id).json} for team in teams]
    return render_template('check_in_assistant/tournament_check_in.html', teams=teams)


@bp.route('/check_in_dancer/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def check_in_dancer(number):
    dancer = db.session.query(Contestant).join(StatusInfo, ContestantInfo)\
        .filter(Contestant.contestant_id == number).first()
    if dancer.contestant_info.team_captain is True and dancer.status_info.checked_in is False:
        dancers_unpaid = db.session.query(Contestant).join(ContestantInfo, StatusInfo)\
            .filter(ContestantInfo.team == dancer.contestant_info.team, StatusInfo.status == CONFIRMED,
                    StatusInfo.paid.is_(False)).order_by(ContestantInfo.number).all()
        if len(dancers_unpaid) > 0:
            flash(Markup('There are dancers that have not paid their entree fee and/or merchandise. '
                         'Please click <a href="{url}" target="_blank">here</a> to check the finances tab, or use the '
                         'list below.'.format(url=url_for('organizer.finances_overview'))), 'alert-danger')
        else:
            finances = TeamFinancialOverview(User.query.filter(User.team == dancer.contestant_info.team,
                                                               User.access == ACCESS[TEAM_CAPTAIN]).first())\
                .finances_overview()
            if dancer.contestant_info.team.amount_paid != finances['price_total']:
                flash(Markup('There is a discrepancy with the total amount owed and total amount received. '
                      'Please click <a href="{url}" target="_blank">here</a> to check the finances tab, or use the '
                             'list below'.format(url=url_for('organizer.finances_overview'))), 'alert-danger')
    dancer.status_info.checked_in = True if dancer.status_info.checked_in is False else False
    db.session.commit()
    if dancer.status_info.checked_in:
        flash('{name} from team {team} has been checked in.'
              .format(name=dancer.get_full_name(), team=dancer.contestant_info.team), 'alert-success')
        if not dancer.status_info.paid:
            flash('Payment of the entry fee and/or merchandise for {name} from team {team} has not as marked as paid.'
                  .format(name=dancer.get_full_name(), team=dancer.contestant_info.team), 'alert-warning')
    else:
        flash('{name} from team {team} has been checked out.'
              .format(name=dancer.get_full_name(), team=dancer.contestant_info.team))
    return redirect(url_for('organizer.tournament_check_in'))


@bp.route('/dancer_paid/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def dancer_paid(number):
    dancer = db.session.query(Contestant).join(StatusInfo).filter(Contestant.contestant_id == number).first()
    dancer.status_info.paid = True if dancer.status_info.paid is False else False
    db.session.commit()
    flash('Payment status of {name} from team {team} changed successfully.'
          .format(name=dancer.get_full_name(), team=dancer.contestant_info.team))
    return redirect(url_for('organizer.tournament_check_in'))
