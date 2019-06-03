from flask import render_template, request, flash, redirect, url_for, send_file, g, Markup
from flask_login import login_required, logout_user, login_user
from ntds_webportal import db
from ntds_webportal.organizer import bp
from ntds_webportal.models import requires_access_level, Team, Contestant, ContestantInfo, DancingInfo,\
    StatusInfo, AdditionalInfo, NameChangeRequest, User, MerchandiseInfo, VolunteerInfo, \
    requires_tournament_state, SuperVolunteer, Adjudicator, PaymentInfo, MerchandiseItem, MerchandiseItemVariant, \
    MerchandisePurchase
from ntds_webportal.functions import submit_updated_dancing_info, random_password, active_teams, competing_teams
from ntds_webportal.organizer.forms import NameChangeResponse, ChangeEmailForm, FinalizeMerchandiseForm, \
    CreateNewMerchandiseForm
from ntds_webportal.self_admin.forms import CreateBaseUserWithoutEmailForm, EditAssistantAccountForm, \
    MerchandiseDateForm
from ntds_webportal.organizer.email import send_registration_open_email, send_gdpr_reminder_email
from ntds_webportal.teamcaptains.forms import EditDancingInfoForm
from ntds_webportal.auth.email import send_team_captain_activation_email
import ntds_webportal.data as data
from ntds_webportal.data import *
from sqlalchemy import or_, case
import xlsxwriter
from io import BytesIO, StringIO
import datetime


@bp.route('/manage_merchandise', methods=['GET', "POST"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def manage_merchandise():
    all_merchandise = MerchandiseItem.query.all()
    form = CreateNewMerchandiseForm()
    merchandise_date_form = MerchandiseDateForm()
    if request.method == "GET":
        mcd = datetime.datetime.utcfromtimestamp(g.sc.merchandise_closing_date).replace(tzinfo=datetime.timezone.utc)
        mcd += datetime.timedelta(days=-1)
        merchandise_date_form.merchandise_closing_date.data = datetime.date(mcd.year, mcd.month, mcd.day)
    purchases = sorted(MerchandisePurchase.query.all(),
                       key=lambda x: (x.merchandise_info.contestant.contestant_info.team.display_name(),
                                      x.merchandise_info.contestant.get_full_name()))
    if request.method == "POST":
        if merchandise_date_form.merchandise_closing_submit.name in request.form:
            if merchandise_date_form.validate_on_submit():
                mcd = datetime.datetime(merchandise_date_form.merchandise_closing_date.data.year,
                                        merchandise_date_form.merchandise_closing_date.data.month,
                                        merchandise_date_form.merchandise_closing_date.data.day, 3, 0, 0, 0)\
                    .replace(tzinfo=datetime.timezone.utc)
                mcd += datetime.timedelta(days=1)
                g.sc.merchandise_closing_date = mcd.timestamp()
                db.session.commit()
                flash(f"Merchandise closing date set.", 'alert-success')
                return redirect(url_for('organizer.manage_merchandise'))
        if "cancel_purchase" in request.form:
            purchase = MerchandisePurchase.query\
                .filter(MerchandisePurchase.merchandise_purchased_id == request.form["cancel_purchase"]).first()
            purchase.cancel(show_flash_messages=True)
            return redirect(url_for('organizer.manage_merchandise'))
        if "reinstate_purchase" in request.form:
            purchase = MerchandisePurchase.query\
                .filter(MerchandisePurchase.merchandise_purchased_id == request.form["reinstate_purchase"]).first()
            purchase.cancelled = False
            db.session.commit()
            flash(f"Order for {purchase} has been reinstated.")
            return redirect(url_for('organizer.manage_merchandise'))
        if not g.ts.merchandise_finalized:
            if form.new_item_submit.name in request.form:
                if form.validate_on_submit():
                    variants = form.variants.data.split(",")
                    if form.shirt.data == "shirt":
                        for var in variants:
                            item = MerchandiseItem(description=f"{var.strip()} {form.item.data}", price=form.price.data)
                            item.shirt = True
                            for size in SHIRT_SIZES:
                                item.variants.append(MerchandiseItemVariant(variant=size, merchandise_item=item))
                            db.session.add(item)
                            db.session.commit()
                            flash(f"{item.description} added.", 'alert-success')
                    else:
                        item = MerchandiseItem(description=form.item.data, price=form.price.data)
                        for var in variants:
                            item.variants.append(MerchandiseItemVariant(variant=var.strip(), merchandise_item=item))
                        db.session.add(item)
                        db.session.commit()
                        flash(f"{item.description} added.", 'alert-success')
                    return redirect(url_for('organizer.manage_merchandise'))
            if "delete" in request.form:
                var = MerchandiseItemVariant.query\
                    .filter(MerchandiseItemVariant.merchandise_item_variant_id == request.form["delete"]).first()
                if len(var.merchandise_item.variants) > 1:
                    flash(f"Deleted {var.variant_name()} variant of {var.merchandise_item}.", 'alert-success')
                    db.session.delete(var)
                    db.session.commit()
                    return redirect(url_for('organizer.manage_merchandise'))
                else:
                    flash(f"Cannot delete the last variant of {var.merchandise_item}.", 'alert-warning')
            if "add" in request.form:
                merchandise_item = MerchandiseItem.query \
                    .filter(MerchandiseItem.merchandise_item_id == request.form["add"]).first()
                if len(request.form["new_variant"].strip()) > 0:
                    var = MerchandiseItemVariant(variant=request.form["new_variant"].strip(),
                                                 merchandise_item=merchandise_item)
                    merchandise_item.variants.append(var)
                    flash(f"Added {var.variant_name()} variant to {var.merchandise_item}.", 'alert-success')
                    db.session.commit()
                    return redirect(url_for('organizer.manage_merchandise'))
                else:
                    flash(f"Cannot add a variant without a name.", 'alert-warning')
            if "merchandise_item" in request.form:
                merchandise_item = MerchandiseItem.query\
                    .filter(MerchandiseItem.merchandise_item_id == request.form["merchandise_item"]).first()
                merchandise_item.description = request.form[form.item.name]
                merchandise_item.price = int(request.form[form.price.name])
                if not merchandise_item.shirt:
                    for var in merchandise_item.variants:
                        var.variant = request.form[str(var.merchandise_item_variant_id)]
                db.session.commit()
                flash(f"{merchandise_item} updated,", 'alert-success')
                return redirect(url_for('organizer.manage_merchandise'))
    return render_template('organizer/manage_merchandise.html', form=form, all_merchandise=all_merchandise,
                           merchandise_date_form=merchandise_date_form, purchases=purchases)
#
#
# @bp.route('/cancel_purchase/<int:purchase_id>', methods=["DELETE"])
# @login_required
# @requires_access_level([ACCESS[ORGANIZER]])
# @requires_tournament_state(SYSTEM_CONFIGURED)
# def cancel_purchase(purchase_id):
#     purchase = MerchandisePurchase.query.filter(MerchandisePurchase.merchandise_purchased_id == purchase_id).first()
#     if request.method == "DELETE":
#         if purchase.cancel():
#             return purchase_id
#     return 0


@bp.route('/user_list', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def user_list():
    if request.method == "POST":
        if 'activate_teamcaptains' in request.form:
            team_captains = User.query.join(Team).filter(User.access == ACCESS[TEAM_CAPTAIN], User.activate.is_(True))
            if g.sc.tournament == NTDS:
                team_captains = team_captains.filter(Team.country == NETHERLANDS).all()
            else:
                team_captains = team_captains.all()
            for tc in team_captains:
                if tc.email is not None:
                    tc.is_active = True
                    tc_pass = random_password()
                    tc.set_password(tc_pass)
                    send_team_captain_activation_email(tc.email, tc, tc_pass,
                                                       tournament=g.sc.tournament, year=g.sc.year, city=g.sc.city)
            g.ts.website_accessible_to_teamcaptains = True
            db.session.commit()
            message = f"The accounts for all team captains{f' from {NETHERLANDS}' if g.sc.tournament == NTDS else ''} "\
                f"have been activated.<br/><br/>An e-mail with the login credentials has been sent to all teamcaptains."
            flash(Markup(message), "alert-success")
            return redirect(url_for('main.dashboard'))
    if not g.ts.website_accessible_to_teamcaptains:
        users = User.query.join(Team).filter(User.access == ACCESS[TEAM_CAPTAIN])
    else:
        users = User.query.join(Team)\
            .filter(or_(User.access == ACCESS[TEAM_CAPTAIN], User.access == ACCESS[TREASURER]))
    if g.sc.tournament == NTDS:
        users = users.filter(Team.country == NETHERLANDS).all()
    else:
        users = users.all()
    users = {u.user_id: u.json() for u in users}
    bda = db.session.query(User).filter(User.access == ACCESS[BLIND_DATE_ASSISTANT]).first()
    chi = db.session.query(User).filter(User.access == ACCESS[CHECK_IN_ASSISTANT]).first()
    ada = db.session.query(User).filter(User.access == ACCESS[ADJUDICATOR_ASSISTANT]).first()
    tom = db.session.query(User).filter(User.access == ACCESS[TOURNAMENT_OFFICE_MANAGER]).first()
    fm = db.session.query(User).filter(User.access == ACCESS[FLOOR_MANAGER]).first()
    return render_template('organizer/user_list.html', users=users, bda=bda, chi=chi, ada=ada, tom=tom, fm=fm)


def assistant_account(access_level):
    submit = False
    user = db.session.query(User).filter(User.access == ACCESS[access_level]).first()
    if user is None:
        form = CreateBaseUserWithoutEmailForm()
        if access_level == BLIND_DATE_ASSISTANT:
            form.username.data = BLIND_DATE_ASSISTANT_ACCOUNT_NAME
        elif access_level == CHECK_IN_ASSISTANT:
            form.username.data = CHECK_IN_ASSISTANT_ACCOUNT_NAME
        elif access_level == ADJUDICATOR_ASSISTANT:
            form.username.data = ADJUDICATOR_ASSISTANT_ACCOUNT_NAME
        elif access_level == TOURNAMENT_OFFICE_MANAGER:
            form.username.data = TOURNAMENT_OFFICE_MANAGER_ACCOUNT_NAME
        elif access_level == FLOOR_MANAGER:
            form.username.data = FLOOR_MANAGER_ACCOUNT_NAME
        if form.validate_on_submit():
            user = User()
            user.username = form.username.data
            user.set_password(form.password.data)
            user.access = ACCESS[access_level]
            user.is_active = True
            user.send_new_messages_email = False
            db.session.add(user)
            db.session.commit()
            flash(f"Assistant account \"{user.username}\" created.", 'alert-success')
            submit = True
    else:
        form = EditAssistantAccountForm()
        form.username.data = user.username
        if form.validate_on_submit():
            if form.password.data != '':
                user.set_password(form.password.data)
                db.session.commit()
                flash(f"Assistant account \"{user.username}\" updated.", 'alert-success')
            else:
                flash(f"No changes were made to save.", "alert-warning")
            submit = True
    return form, user, submit


@bp.route('/blind_date_assistant_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def blind_date_assistant_account():
    form, user, submit = assistant_account(BLIND_DATE_ASSISTANT)
    if submit:
        return redirect(url_for('organizer.user_list'))
    return render_template('organizer/assistant_account.html', form=form, user=user, assistant=BLIND_DATE_ASSISTANT)


@bp.route('/check_in_assistant_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def check_in_assistant_account():
    form, user, submit = assistant_account(CHECK_IN_ASSISTANT)
    if submit:
        return redirect(url_for('organizer.user_list'))
    return render_template('organizer/assistant_account.html', form=form, user=user, assistant=CHECK_IN_ASSISTANT)


@bp.route('/adjudicator_assistant_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def adjudicator_assistant_account():
    form, user, submit = assistant_account(ADJUDICATOR_ASSISTANT)
    if submit:
        return redirect(url_for('organizer.user_list'))
    return render_template('organizer/assistant_account.html', form=form, user=user, assistant=ADJUDICATOR_ASSISTANT)


@bp.route('/tournament_office_manager_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def tournament_office_manager_account():
    form, user, submit = assistant_account(TOURNAMENT_OFFICE_MANAGER)
    if submit:
        return redirect(url_for('organizer.user_list'))
    return render_template('organizer/assistant_account.html', form=form, user=user,
                           assistant=TOURNAMENT_OFFICE_MANAGER)


@bp.route('/floor_manager_account', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def floor_manager_account():
    form, user, submit = assistant_account(FLOOR_MANAGER)
    if submit:
        return redirect(url_for('organizer.user_list'))
    return render_template('organizer/assistant_account.html', form=form, user=user, assistant=FLOOR_MANAGER)


@bp.route('/change_email/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def change_email(number):
    user = User.query.filter(User.user_id == number).first()
    form = ChangeEmailForm()
    if request.method == 'GET':
        form.email.data = user.email
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.commit()
        flash(f"Changed e-mail of {user.username} to {form.email.data}.", 'alert-success')
        return redirect(url_for('organizer.user_list'))
    return render_template('admin/change_email.html', form=form, user=user)


@bp.route('/registration_management', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(TEAM_CAPTAINS_HAVE_ACCESS)
def registration_management():
    no_gdpr_dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == NO_GDPR)\
        .order_by(Contestant.first_name).all()
    form = request.args
    if 'start_registration_period' in form:
        g.ts.registration_period_started = True
        g.ts.registration_open = True
        g.sc.system_configuration_accessible = False
        team_captains = User.query.filter(User.access == ACCESS[TEAM_CAPTAIN], User.is_active.is_(True)).all()
        for tc in team_captains:
            send_registration_open_email(tc.email)
        admin = User.query.filter(User.access == ACCESS[ADMIN]).first()
        send_registration_open_email(admin.email)
        flash(f"Registration for the {g.sc.tournament} has started!", "alert-success")
    if 'close_registration' in form:
        g.ts.registration_open = False
        flash(f"Registration for the {g.sc.tournament} has been closed.", "alert-info")
    if 'open_registration' in form:
        g.ts.registration_open = True
        flash(f"Registration for the {g.sc.tournament} has been opened again.", "alert-info")
    if 'notify_no_gdpr' in form:
        for dancer in no_gdpr_dancers:
            send_gdpr_reminder_email(dancer)
        flash(f"Reminder for accepting the privacy policy has been sent to the dancers in question.", "alert-info")
    if len(form) > 0:
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('organizer/registration_management.html', no_gdpr_dancers=no_gdpr_dancers)


@bp.route('/registration_overview', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def registration_overview():
    all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
        .order_by(ContestantInfo.team_id,
                  case({CONFIRMED: 0, SELECTED: 1, REGISTERED: 2, CANCELLED: 3}, value=StatusInfo.status),
                  Contestant.first_name).all()
    all_teams = active_teams()
    dancers = [{'country': team.country, 'name': team.display_name(), 'id': team.city,
                'dancers': len(Contestant.query.join(ContestantInfo).filter(ContestantInfo.team == team)
                               .order_by(Contestant.first_name).all())} for team in all_teams]
    dutch_dancers = [team for team in dancers if team['country'] == NETHERLANDS]
    german_dancers = [team for team in dancers if team['country'] == GERMANY]
    other_dancers = [team for team in dancers if team['country'] != NETHERLANDS and team['country'] != GERMANY]
    return render_template('organizer/registration_overview.html', all_dancers=all_dancers,
                           dutch_dancers=dutch_dancers, german_dancers=german_dancers, other_dancers=other_dancers)


@bp.route('/view_dancer/<int:number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def view_dancer(number):
    dancer = Contestant.query.filter(Contestant.contestant_id == number).first()
    return render_template('organizer/view_dancer.html', dancer=dancer)


@bp.route('/name_change_list', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def name_change_list():
    nml_open = NameChangeRequest.query.filter(NameChangeRequest.state == NameChangeRequest.STATE['Open']).all()
    nml_closed = NameChangeRequest.query.filter(NameChangeRequest.state != NameChangeRequest.STATE['Open']).all()
    return render_template('organizer/name_change_list.html', nml_open=nml_open, nml_closed=nml_closed)


@bp.route('/name_change_respond/<req>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(REGISTRATION_STARTED)
def name_change_respond(req):
    req = NameChangeRequest.query.filter_by(id=req).first()
    if not req:
        return redirect('error.404')
    form = NameChangeResponse()
    if form.validate_on_submit():
        accepted = form.accept.data
        req.response = form.remark.data
        if accepted:
            flash('Name change request accepted')
            req.accept()
        else:
            flash('Name change request rejected')
            req.reject()
        db.session.commit()
        return redirect(url_for('organizer.name_change_list'))
    return render_template('organizer/name_change_respond.html', req=req, form=form)


@bp.route('/dancing_info_list', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[BLIND_DATE_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def dancing_info_list():
    dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo) \
        .filter(or_(StatusInfo.status == CONFIRMED, StatusInfo.status == SELECTED))\
        .order_by(ContestantInfo.team_id, Contestant.first_name).all()
    return render_template('organizer/dancing_info_list.html', data=data, dancers=dancers)


@bp.route('/edit_dancing_info/<number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[BLIND_DATE_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def edit_dancing_info(number):
    dancer = db.session.query(Contestant).join(DancingInfo).filter(Contestant.contestant_id == number).first()
    form = EditDancingInfoForm(dancer)
    if request.method == GET:
        form.populate(dancer)
    if request.method == POST:
        form.custom_validate()
        if form.validate_on_submit():
            flash('{} data has been changed successfully.'.format(submit_updated_dancing_info(form, contestant=dancer)),
                  'alert-success')
            return redirect(url_for('organizer.dancing_info_list'))
    return render_template('organizer/edit_dancing_info.html', data=data, form=form, dancer=dancer)


@bp.route('/finances_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def finances_overview():
    all_teams = competing_teams()
    if g.sc.tournament == NTDS:
        all_teams = all_teams.filter(Team.country == NETHERLANDS).all()
    else:
        all_teams = all_teams.all()
    if request.method == "POST":
        if 'download_file' in request.form:
            download_teams = [{
                'team': team,
                'name': team.display_name(),
                'dancers': team.check_in_dancers(),
            } for team in all_teams]
            download_teams = [team for team in download_teams if len(team['dancers']) > 0]
            header = {'Team': 0, '# Dancers': 1, 'Owed': 2, 'Received': 3, 'Difference': 4, 'Refund': 5}
            fn = f'finances_overview_{g.sc.tournament}_{g.sc.city}_{g.sc.year}.xlsx'
            output = BytesIO()
            wb = xlsxwriter.Workbook(output, {'in_memory': True})
            f = wb.add_format({'text_wrap': True, 'bold': True})
            acc = wb.add_format({'num_format': 44})
            total_acc = wb.add_format({'num_format': 44, 'bold': True})
            ws = wb.add_worksheet(name=datetime.date.today().strftime("%B %d, %Y"))
            for name, index in header.items():
                ws.write(0, index, name, f)
            ws.set_column(0, 0, 30)
            ws.set_column(1, 1, 10)
            ws.set_column(2, 5, 15)
            totals = {'dancers': 0, 'owed': 0, 'received': 0, 'difference': 0, 'refund': 0}
            for i, team in enumerate(download_teams, 1):
                owed = sum([d.payment_info.payment_price() for d in team['dancers']])
                received = team['team'].amount_paid
                difference = received - owed
                refund = sum([d.payment_info.refund_price() for d in team['dancers']])
                ws.write(i, 0, team['team'].name)
                ws.write(i, 1, len(team['dancers']))
                ws.write(i, 2, round(owed / 100, 2), acc)
                ws.write(i, 3, round(received / 100, 2), acc)
                ws.write(i, 4, round(difference / 100, 2), acc)
                ws.write(i, 5, round(refund / 100, 2), acc)
                totals['dancers'] += len(team['dancers'])
                totals['owed'] += owed
                totals['received'] += received
                totals['refund'] += refund
            totals['difference'] = totals['received'] - totals['owed']
            ws.write(len(download_teams) + 1, 1, totals['dancers'], wb.add_format({'bold': True}))
            ws.write(len(download_teams) + 1, 2, round(totals['owed'] / 100, 2), total_acc)
            ws.write(len(download_teams) + 1, 3, round(totals['received'] / 100, 2), total_acc)
            ws.write(len(download_teams) + 1, 4, round(totals['difference'] / 100, 2), total_acc)
            ws.write(len(download_teams) + 1, 5, round(totals['refund'] / 100, 2), total_acc)
            ws.freeze_panes(1, 0)
            wb.close()
            output.seek(0)
            return send_file(output, as_attachment=True, attachment_filename=fn)
    teams = {team.team_id: {
        "team_id": team.team_id,
        "country": team.country,
        "name": team.display_name(),
        "finances_data": team.finances_data(view_only=True)
    } for team in all_teams}
    return render_template('organizer/finances_overview.html', teams=teams)


@bp.route('/remove_payment_requirement/<int:number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def remove_payment_requirement(number):
    dancer = StatusInfo.query.filter(StatusInfo.contestant_id == number).first()
    dancer.remove_payment_requirement()
    return redirect(url_for('organizer.finances_overview'))


@bp.route('/add_refund/<int:number>', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def add_refund(number):
    dancer = PaymentInfo.query.filter(PaymentInfo.contestant_id == number).first()
    dancer.set_refund()
    return redirect(url_for('organizer.finances_overview'))


@bp.route('/merchandise', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[CHECK_IN_ASSISTANT]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def merchandise():
    current_timestamp = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    form = FinalizeMerchandiseForm()
    dancers = Contestant.query.join(StatusInfo)\
        .filter(or_(StatusInfo.status == CONFIRMED, StatusInfo.status == CANCELLED)).all()
    dancers = [dancer for dancer in dancers if dancer.merchandise_info.ordered_merchandise()]
    if request.method == "POST":
        if form.submit.name in request.form:
            if form.validate_on_submit():
                if not g.ts.merchandise_finalized:
                    registered_dancers = Contestant.query.join(StatusInfo)\
                        .filter(or_(StatusInfo.status == REGISTERED, StatusInfo.status == NO_GDPR,
                                    StatusInfo.status == CANCELLED)).all()
                    registered_dancers = [d for d in registered_dancers if d.merchandise_info.ordered_merchandise()]
                    for dancer in registered_dancers:
                        dancer.merchandise_info.cancel_merchandise()
                    g.ts.merchandise_finalized = True
                    flash("Merchandise finalized.", "alert-success")
                    db.session.commit()
    all_merchandise = {m: {v: [] for v in m.variants} for m in MerchandiseItem.query.all()}
    for d in dancers:
        for m in d.merchandise_info.purchases:
            all_merchandise[m.merchandise_item_variant.merchandise_item][m.merchandise_item_variant].append(m)
    total_merchandise = {m: sum([len(all_merchandise[m][v]) for v in m.variants]) for m in MerchandiseItem.query.all()}
    dancers = {d.contestant_id: d.json() for d in dancers}
    return render_template('organizer/merchandise.html', dancers=dancers, current_timestamp=current_timestamp,
                           form=form, all_merchandise=all_merchandise, total_merchandise=total_merchandise)


@bp.route('/sleeping_hall', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def sleeping_hall():
    team_captains = db.session.query(User).filter(User.access == ACCESS[TEAM_CAPTAIN], User.is_active.is_(True))\
        .order_by(User.username).all()
    teams = [{'city': team_captain.team.city,
              'number_of_dancers': db.session.query(Contestant).join(ContestantInfo, StatusInfo, AdditionalInfo)
             .filter(ContestantInfo.team == team_captain.team, StatusInfo.status == CONFIRMED,
                     AdditionalInfo.sleeping_arrangements.is_(True)).all()} for team_captain in team_captains]
    super_volunteers = SuperVolunteer.query.filter(SuperVolunteer.sleeping_arrangements.is_(True)).all()
    total = sum([len(team['number_of_dancers']) for team in teams]) + len(super_volunteers)
    form = request.args
    if 'download_file' in form:
        fn = f'sleeping_hall_{g.sc.tournament}_{g.sc.city}_{g.sc.year}.xlsx'
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        f = wb.add_format({'text_wrap': True, 'bold': True})
        la = wb.add_format({'align': 'left'})
        ws = wb.add_worksheet(name='Summary')
        ws.write(0, 0, 'Team', f)
        ws.write(0, 1, 'People in sleeping hall (Total: {total})'.format(total=total), f)
        for d in range(0, len(teams)):
            ws.write(d + 1, 0, teams[d]['city'])
            ws.write(d + 1, 1, len(teams[d]['number_of_dancers']), la)
        ws.write(len(teams) + 1, 0, 'Super Volunteers')
        ws.write(len(teams) + 1, 1, len(super_volunteers), la)
        ws.set_column(0, 0, 30)
        ws.set_column(1, 1, 40)
        ws.freeze_panes(1, 0)
        ws = wb.add_worksheet(name='People in Sleeping Hall')
        ws.write(0, 0, 'Name', f)
        ws.write(0, 1, 'Team', f)
        dancers = sorted(Contestant.query.join(StatusInfo, AdditionalInfo, ContestantInfo)
                         .filter(StatusInfo.status == CONFIRMED, AdditionalInfo.sleeping_arrangements.is_(True)).all(),
                         key=lambda x: x.contestant_info.team.city)
        for i, p in enumerate(dancers, 1):
            ws.write(i, 0, p.get_full_name())
            ws.write(i, 1, p.contestant_info.team.city)
        for i, p in enumerate(super_volunteers, len(dancers) + 1):
            ws.write(i, 0, p.get_full_name())
            ws.write(i, 1, 'Super Volunteer')
        ws.set_column(0, 0, 40)
        ws.set_column(1, 1, 30)
        ws.freeze_panes(1, 0)
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename=fn)
    return render_template('organizer/sleeping_hall.html', teams=teams, super_volunteers=super_volunteers, total=total)


@bp.route('/diet_allergies', methods=[GET, POST])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def diet_allergies():
    dancers = Contestant.query.join(ContestantInfo, StatusInfo).filter(StatusInfo.status == CONFIRMED,
                                                                       ContestantInfo.diet_allergies != "").all()
    dancers = [d for d in dancers if d.contestant_info.diet_allergies.strip() != ""
               and d.contestant_info.diet_allergies != "-"]
    people = [{'id': 'd-' + str(d.contestant_id), 'name': d.get_full_name(), 'diet': d.contestant_info.diet_allergies,
               'notes': d.contestant_info.organization_diet_notes} for d in dancers]
    super_volunteers = SuperVolunteer.query.filter(SuperVolunteer.diet_allergies != "").all()
    super_volunteers = [sv for sv in super_volunteers if sv.diet_allergies.strip() != "" and sv.diet_allergies != "-"]
    people.extend([{'id': 'sv-' + str(sv.volunteer_id), 'name': sv.get_full_name(), 'diet': sv.diet_allergies,
                    'notes': sv.organization_diet_notes} for sv in super_volunteers])
    people.sort(key=lambda x: x['name'])
    old_notes = [p['notes'] for p in people if p['notes'].strip() != ""]
    all_confirmed_dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == CONFIRMED).all()
    all_super_volunteers = SuperVolunteer.query.all()
    total = len(all_confirmed_dancers) + len(all_super_volunteers)
    no_special_diet = total - len(people)
    form = request.args
    if 'download_file' in form:
        fn = f'diet_allergies_{g.sc.tournament}_{g.sc.city}_{g.sc.year}.xlsx'
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        f = wb.add_format({'text_wrap': True, 'bold': True})
        ws = wb.add_worksheet()
        ws.write(0, 0, 'Who?', f)
        ws.write(0, 1, 'Diet/Allergies (Total: {total})'.format(total=len(people)), f)
        for p in range(0, len(people)):
            ws.write(p + 1, 0, people[p]['name'])
            ws.write(p + 1, 1, people[p]['diet'])
        ws.set_column(0, 0, 30)
        ws.set_column(1, 1, 80)
        ws.freeze_panes(1, 0)
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename=fn)
    if request.method == 'POST':
        if 'submit' in request.form:
            changes = False
            for p in people:
                diet_notes = request.form.get(p['id'])
                if p['id'].split('-')[0] == "d":
                    person = ContestantInfo.query.get(int(p['id'].split('-')[1]))
                else:
                    person = SuperVolunteer.query.get(int(p['id'].split('-')[1]))
                if person.organization_diet_notes != diet_notes:
                    person.organization_diet_notes = diet_notes
                    changes = True
            if changes:
                db.session.commit()
                flash('Changes saved successfully.', 'alert-success')
            else:
                flash('No changes were made to submit.', 'alert-warning')
            return redirect(url_for('organizer.diet_allergies'))
    return render_template('organizer/diet_allergies.html',
                           people=people, total=total, no_special_diet=no_special_diet, old_notes=old_notes)


@bp.route('/badges', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def badges():
    dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status != CANCELLED).all()
    dancers.sort(key=lambda x: (x.contestant_info.team.name, x.contestant_info.number))
    confirmed_dancers = [d for d in dancers if d.status_info.status == CONFIRMED]
    remaining_dancers = [d for d in dancers if d.status_info.status != CONFIRMED]
    super_volunteers = SuperVolunteer.query.all()
    return render_template('organizer/badges.html', confirmed_dancers=confirmed_dancers,
                           super_volunteers=super_volunteers, remaining_dancers=remaining_dancers)


@bp.route('/numbers', methods=['GET'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def numbers():
    team_captains = db.session.query(User).filter(User.access == ACCESS[TEAM_CAPTAIN], User.is_active.is_(True))\
        .order_by(User.username).all()
    teams = \
        [{'city': team_captain.team.city, 'number_of_dancers':
            [c for c in Contestant.query.join(ContestantInfo, StatusInfo, AdditionalInfo)
                .filter(ContestantInfo.team == team_captain.team, StatusInfo.status == CONFIRMED)
                .order_by(ContestantInfo.number).all()
             if c.status_info.dancing_lead()]} for team_captain in team_captains]
    return render_template('organizer/numbers.html', teams=teams)


@bp.route('/view_super_volunteer/<int:number>', methods=[GET])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def view_super_volunteer(number):
    super_volunteer = SuperVolunteer.query.filter(SuperVolunteer.volunteer_id == number).first()
    return render_template('organizer/view_super_volunteer.html', super_volunteer=super_volunteer)


@bp.route('/adjudicators_overview', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER], ACCESS[ADJUDICATOR_ASSISTANT], ACCESS[TOURNAMENT_OFFICE_MANAGER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def adjudicators_overview():
    adjudicators = Contestant.query.join(VolunteerInfo, StatusInfo, ContestantInfo) \
        .filter(StatusInfo.status == CONFIRMED, or_(VolunteerInfo.jury_ballroom != NO, VolunteerInfo.jury_latin != NO))\
        .order_by(Contestant.first_name).all()
    super_volunteer_adjudicators = SuperVolunteer.query\
        .filter(or_(SuperVolunteer.jury_ballroom != NO, SuperVolunteer.jury_latin != NO))\
        .order_by(SuperVolunteer.first_name).all()
    selected_adjudicators = [a for a in adjudicators if a.volunteer_info.selected_adjudicator] + \
                            [a for a in super_volunteer_adjudicators if a.selected_adjudicator]
    form = request.form
    tags = generate_tags(adjudicators + super_volunteer_adjudicators)
    if request.method == POST:
        if 'submit' in form:
            submitted_tags = [form.get(f"tag-contestant-{a.contestant_id}") for a in adjudicators] + \
                             [form.get(f"tag-super_volunteer-{a.volunteer_id}") for a in super_volunteer_adjudicators]
            if sorted(set(tags.values())) == sorted(set(submitted_tags)):
                for adjudicator in adjudicators:
                    adjudicator.volunteer_info.selected_adjudicator = \
                        f"checked-contestant-{adjudicator.contestant_id}" in form
                    adjudicator.volunteer_info.adjudicator_notes = form.get(f"contestant-{adjudicator.contestant_id}")
                    if adjudicator.volunteer_info.selected_adjudicator:
                        check_adjudicator = Adjudicator.query\
                            .filter(Adjudicator.name == adjudicator.get_full_name()).first()
                        if check_adjudicator is None:
                            new_adjudicator = Adjudicator()
                            new_adjudicator.name = adjudicator.get_full_name()
                            new_adjudicator.tag = form.get(f"tag-contestant-{adjudicator.contestant_id}")
                            new_adjudicator.user = adjudicator.user
                            db.session.add(new_adjudicator)
                        else:
                            if adjudicator.user.adjudicator is not None:
                                adjudicator.user.adjudicator.name = adjudicator.get_full_name()
                                adjudicator.user.adjudicator.tag = \
                                    form.get(f"tag-contestant-{adjudicator.contestant_id}")
                    else:
                        adjudicator.user.adjudicator = None
                for adjudicator in super_volunteer_adjudicators:
                    adjudicator.selected_adjudicator = f"checked-super_volunteer-{adjudicator.volunteer_id}" in form
                    adjudicator.adjudicator_notes = form.get(f"super_volunteer-{adjudicator.volunteer_id}")
                    if adjudicator.selected_adjudicator:
                        check_adjudicator = Adjudicator.query\
                            .filter(Adjudicator.name == adjudicator.get_full_name()).first()
                        if check_adjudicator is None:
                            new_adjudicator = Adjudicator()
                            new_adjudicator.name = adjudicator.get_full_name()
                            new_adjudicator.tag = form.get(f"tag-super_volunteer-{adjudicator.volunteer_id}")
                            new_adjudicator.user = adjudicator.user
                            db.session.add(new_adjudicator)
                        else:
                            if adjudicator.user.adjudicator is not None:
                                adjudicator.user.adjudicator.name = adjudicator.get_full_name()
                                adjudicator.user.adjudicator.tag = \
                                    form.get(f"tag-super_volunteer-{adjudicator.volunteer_id}")
                    else:
                        adjudicator.user.adjudicator = None
                for adjudicator in Adjudicator.query.all():
                    if adjudicator.user is None:
                        db.session.delete(adjudicator)
                db.session.commit()
                flash('Changes saved.', 'alert-success')
                return redirect(url_for('organizer.adjudicators_overview'))
            else:
                flash("Adjudicator tags are not unique.", "alert-warning")
    form = request.args
    if 'download_file' in form:
        fn = f'adjudicators_{g.sc.tournament}_{g.sc.city}_{g.sc.year}.xlsx'
        output = BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        f = wb.add_format({'text_wrap': True, 'bold': True})
        ws = wb.add_worksheet(name="adjudicators")
        ws.write(0, 0, 'Selected to adjudicate', f)
        ws.write(0, 1, 'Dancer', f)
        ws.write(0, 2, 'Team', f)
        ws.write(0, 3, 'E-mail', f)
        ws.write(0, 4, 'Wants to adjudicate Ballroom?', f)
        ws.write(0, 5, 'Has Ballroom license?', f)
        ws.write(0, 6, 'Highest achieved level in Ballroom', f)
        ws.write(0, 7, 'Wants to adjudicate Latin?', f)
        ws.write(0, 8, 'Has Latin license?', f)
        ws.write(0, 9, 'Highest achieved level in Latin', f)
        ws.write(0, 10, 'Dancing Ballroom?', f)
        ws.write(0, 11, 'Dancing Latin?', f)
        if g.sc.polka_competition:
            ws.write(0, 13, 'Wants to adjudicate Polka?', f)
            ws.set_column(12, 12, 0)
            ws.set_column(13, 13, 10)
        if g.sc.salsa_competition:
            ws.write(0, 12, 'Wants to adjudicate Salsa?', f)
            ws.set_column(12, 12, 10)
            ws.set_column(13, 13, 10)
        ws.set_column(0, 0, 10)
        ws.set_column(1, 1, 25)
        ws.set_column(2, 2, 15)
        ws.set_column(3, 3, 35)
        ws.set_column(4, 9, 10)
        ws.set_column(10, 11, 15)
        for i, adj in enumerate(super_volunteer_adjudicators, 1):
            ws.write(i, 0, 'Yes' if adj.selected_adjudicator else '')
            ws.write(i, 1, adj.get_full_name())
            ws.write(i, 2, 'Super Volunteer')
            ws.write(i, 3, adj.email)
            ws.write(i, 4, adj.jury_ballroom)
            ws.write(i, 5, adj.license_jury_ballroom)
            ws.write(i, 6, adj.level_ballroom)
            ws.write(i, 7, adj.jury_latin)
            ws.write(i, 8, adj.license_jury_latin)
            ws.write(i, 9, adj.level_latin)
            ws.write(i, 10, '-')
            ws.write(i, 11, '-')
            if g.sc.salsa_competition:
                ws.write(i, 12, adj.jury_salsa)
            if g.sc.polka_competition:
                ws.write(i, 13, adj.jury_polka)
        for i, adj in enumerate(adjudicators, 1 + len(super_volunteer_adjudicators)):
            ws.write(i, 0, 'Yes' if adj.volunteer_info.selected_adjudicator else '')
            ws.write(i, 1, adj.get_full_name())
            ws.write(i, 2, adj.contestant_info.team.city)
            ws.write(i, 3, adj.email)
            ws.write(i, 4, adj.volunteer_info.jury_ballroom)
            ws.write(i, 5, adj.volunteer_info.license_jury_ballroom)
            ws.write(i, 6, adj.volunteer_info.level_ballroom)
            ws.write(i, 7, adj.volunteer_info.jury_latin)
            ws.write(i, 8, adj.volunteer_info.license_jury_latin)
            ws.write(i, 9, adj.volunteer_info.level_latin)
            ws.write(i, 10, adj.competition(BALLROOM).level)
            ws.write(i, 11, adj.competition(LATIN).level)
            if g.sc.salsa_competition:
                ws.write(i, 12, adj.volunteer_info.jury_salsa)
            if g.sc.polka_competition:
                ws.write(i, 13, adj.volunteer_info.jury_polka)
        ws.freeze_panes(1, 0)
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename=fn)
    return render_template('organizer/adjudicators_overview.html', adjudicators=adjudicators, tags=tags,
                           super_volunteer_adjudicators=super_volunteer_adjudicators,
                           selected_adjudicators=selected_adjudicators)


def generate_tags(adjudicators):
    tags = {a: f"{a.first_name[:2]}{a.last_name[0]}".upper() for a in adjudicators}
    non_unique_tags = list(set([tags[a] for a in adjudicators if list(tags.values()).count(tags[a]) > 1]))
    for tag in non_unique_tags:
        tags_to_modify = {a: tags[a] for a in adjudicators if tags[a] == tag}
        for i, adj in enumerate(tags_to_modify, 1):
            tags[adj] = f"{tags[adj]}{i}"
    return tags


def update_adjudicator(form, adjudicator, selected=False):
    if selected:
        check_adjudicator = Adjudicator.query.filter(Adjudicator.name == adjudicator.get_full_name()).first()
        if check_adjudicator is None:
            new_adjudicator = Adjudicator()
            new_adjudicator.name = adjudicator.get_full_name()
            new_adjudicator.tag = form.get(f"tag-contestant-{adjudicator.contestant_id}")
            new_adjudicator.user = adjudicator.user
            db.session.add(new_adjudicator)
        else:
            if adjudicator.user.adjudicator is not None:
                adjudicator.user.adjudicator.name = adjudicator.get_full_name()
                adjudicator.user.adjudicator.tag = form.get(f"tag-contestant-{adjudicator.contestant_id}")
    else:
        adjudicator.user.adjudicator = None


@bp.route('/BAD', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(SYSTEM_CONFIGURED)
def bad():
    form = request.args
    if 'download_createUniverse' in form:
        output = StringIO(render_template('organizer/_BAD_createUniverse.sql'))
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="createUniverse.sql")
    if 'download_createDB' in form:
        output = StringIO(render_template('organizer/_BAD_createDB.sql'))
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="createDB.sql")
    if 'download_createTournament' in form:
        teams = competing_teams().all()
        dancers = Contestant.query.join(StatusInfo)\
            .filter(or_(StatusInfo.status == SELECTED, StatusInfo.status == CONFIRMED)).all()
        registered_dancers = Contestant.query.join(StatusInfo).filter(StatusInfo.status == REGISTERED).all()
        text = render_template('organizer/_BAD_createTournament.sql', teams=teams, dancers=dancers,
                               registered_dancers=registered_dancers)
        output = StringIO(text)
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="createTournament.sql")
    if 'download_populateCouples' in form:
        leads = Contestant.query.join(StatusInfo).join(DancingInfo) \
            .filter(or_(StatusInfo.status == SELECTED, StatusInfo.status == CONFIRMED), DancingInfo.role == LEAD) \
            .all()
        leads = [di for lead in leads for di in lead.dancing_info if di.role == LEAD and di.partner is not None]
        closed_open_leads = Contestant.query.join(StatusInfo).join(DancingInfo) \
            .filter(or_(StatusInfo.status == SELECTED, StatusInfo.status == CONFIRMED), DancingInfo.role == LEAD,
                    or_(DancingInfo.level == CLOSED, DancingInfo.level == OPEN_CLASS)).all()
        closed_open_leads = [di for lead in closed_open_leads for di in lead.dancing_info if di.role == LEAD
                             and (di.level == CLOSED or di.level == OPEN_CLASS)]
        closed_open_follows = Contestant.query.join(StatusInfo).join(DancingInfo) \
            .filter(or_(StatusInfo.status == SELECTED, StatusInfo.status == CONFIRMED), DancingInfo.role == FOLLOW,
                    or_(DancingInfo.level == CLOSED, DancingInfo.level == OPEN_CLASS)).all()
        closed_open_follows = [di for follow in closed_open_follows for di in follow.dancing_info if di.role == FOLLOW
                               and (di.level == CLOSED or di.level == OPEN_CLASS)]
        text = render_template('organizer/_BAD_populateCouples.sql', leads=leads,
                               closed_open_leads=closed_open_leads, closed_open_follows=closed_open_follows)
        output = StringIO(text)
        output = BytesIO(output.read().encode('utf-8-sig'))
        return send_file(output, as_attachment=True, attachment_filename="populateCouples.sql")
    return render_template('organizer/BAD.html', ts=g.ts)


@bp.route('/switch_to_bda', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def switch_to_bda():
    bda = User.query.filter(User.access == ACCESS[BLIND_DATE_ASSISTANT]).first()
    if bda is not None:
        logout_user()
        login_user(bda)
    else:
        flash('Blind Date Assistant account not created.')
    return redirect(url_for('main.index'))


@bp.route('/switch_to_cia', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def switch_to_cia():
    cia = User.query.filter(User.access == ACCESS[CHECK_IN_ASSISTANT]).first()
    if cia is not None:
        logout_user()
        login_user(cia)
    else:
        flash('Check-in Assistant account not created.')
    return redirect(url_for('main.index'))


@bp.route('/switch_to_ada', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def switch_to_ada():
    ada = User.query.filter(User.access == ACCESS[ADJUDICATOR_ASSISTANT]).first()
    if ada is not None:
        logout_user()
        login_user(ada)
    else:
        flash('Adjudicator Assistant account not created.')
    return redirect(url_for('main.index'))


@bp.route('/switch_to_tom', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def switch_to_tom():
    tom = User.query.filter(User.access == ACCESS[TOURNAMENT_OFFICE_MANAGER]).first()
    if tom is not None:
        logout_user()
        login_user(tom)
    else:
        flash('Tournament Office Manager account not created.')
    return redirect(url_for('main.index'))


@bp.route('/switch_to_fm', methods=['GET', 'POST'])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
@requires_tournament_state(RAFFLE_CONFIRMED)
def switch_to_fm():
    fm = User.query.filter(User.access == ACCESS[FLOOR_MANAGER]).first()
    if fm is not None:
        if g.event is not None:
            logout_user()
            login_user(fm)
        else:
            flash('There is no event yet.')
    else:
        flash('Floor Manager account not created.')
    return redirect(url_for('main.index'))
