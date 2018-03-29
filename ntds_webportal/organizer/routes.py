from flask import render_template
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.organizer import bp
from ntds_webportal.models import Contestant, ContestantInfo, StatusInfo, requires_access_level
import ntds_webportal.data as data


@bp.route('/registration_overview')
@login_required
@requires_access_level([data.ACCESS['organizer']])
def registration_overview():
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .order_by(ContestantInfo.team_id, ContestantInfo.number).all()
    order = [data.CONFIRMED, data.SELECTED, data.REGISTERED, data.CANCELLED]
    all_dancers = sorted(all_dancers, key=lambda o: (o.contestant_info[0].team_id,
                                                     order.index(o.status_info[0].status)))
    dancers = [{'country': team['country'], 'name': team['name'], 'id': team['name'].replace(' ', '-').replace('`', ''),
               'dancers': [dancer for dancer in all_dancers if dancer.contestant_info[0].team.name == team['name']]}
               for team in data.TEAMS]
    dutch_dancers = [team for team in dancers if team['country'] == data.NETHERLANDS]
    german_dancers = [team for team in dancers if team['country'] == data.GERMANY]
    other_dancers = [team for team in dancers if team['country'] != data.NETHERLANDS and
                     team['country'] != data.GERMANY]
    return render_template('organizer/registration_overview.html', data=data, all_dancers=all_dancers,
                           dutch_dancers=dutch_dancers, german_dancers=german_dancers, other_dancers=other_dancers)


@bp.route('/finances_overview')
@login_required
@requires_access_level([data.ACCESS['organizer']])
def finances_overview():
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .filter(StatusInfo.payment_required.is_(True)).order_by(ContestantInfo.team_id, ContestantInfo.number).all()
    all_confirmed_dancers = [d for d in all_dancers if d.status_info[0].status == data.CONFIRMED]
    all_cancelled_dancers = [d for d in all_dancers if d.status_info[0].status == data.CANCELLED]
    all_finances = data.finances_overview(all_dancers)
    dancers = [{'country': team['country'], 'name': team['name'], 'id': team['name'].replace(' ', '-').replace('`', ''),
                'confirmed_dancers': [dancer for dancer in all_confirmed_dancers if
                                      dancer.contestant_info[0].team.name == team['name']],
                'cancelled_dancers': [dancer for dancer in all_cancelled_dancers if
                                      dancer.contestant_info[0].team.name == team['name']],
                'finances': data.finances_overview([dancer for dancer in all_dancers if
                                                    dancer.contestant_info[0].team.name == team['name']])}
               for team in data.TEAMS]
    dutch_dancers = [team for team in dancers if team['country'] == data.NETHERLANDS]
    german_dancers = [team for team in dancers if team['country'] == data.GERMANY]
    other_dancers = [team for team in dancers if team['country'] != data.NETHERLANDS and
                     team['country'] != data.GERMANY]
    return render_template('organizer/finances_overview.html', dancers=dancers,
                           all_confirmed_dancers=all_confirmed_dancers, all_cancelled_dancers=all_cancelled_dancers,
                           dutch_dancers=dutch_dancers, german_dancers=german_dancers, other_dancers=other_dancers,
                           data=data)
