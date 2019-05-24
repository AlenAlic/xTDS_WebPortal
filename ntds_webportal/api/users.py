from flask import jsonify, request, json
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import requires_access_level, User
from ntds_webportal.api import bp
from ntds_webportal.data import *
import re


@bp.route('/users/<int:user_id>/activate/<bool:activate>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def users_activate(user_id, activate):
    user = User.query.get_or_404(user_id)
    if request.method == "PATCH":
        user.activate = activate
        db.session.commit()
    return jsonify(user.json())


@bp.route('/users/<int:user_id>/set_email', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def users_set_email(user_id):
    user = User.query.get_or_404(user_id)
    data = json.loads(request.data)
    if request.method == "PATCH":
        if re.match(r"[^@]+@[^@]+\.[^@]+", data["email"].strip()):
            user.email = data["email"].strip()
            db.session.commit()
    return jsonify(user.json())


@bp.route('/users/<int:user_id>/activate_teamcaptain/<bool:is_active>', methods=["PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def users_activate_teamcaptain(user_id, is_active):
    user = User.query.get_or_404(user_id)
    if request.method == "PATCH":
        user.is_active = is_active
        db.session.commit()
    return jsonify(user.json())
