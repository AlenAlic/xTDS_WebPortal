from flask import jsonify, request
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import requires_access_level, StatusInfo
from ntds_webportal.api import bp
from ntds_webportal.data import *


@bp.route('/status_info/guaranteed_entry/<int:contestant_id>', methods=["GET", "PATCH"])
@login_required
@requires_access_level([ACCESS[ORGANIZER]])
def status_info_guaranteed_entry(contestant_id):
    dancer = StatusInfo.query.filter(StatusInfo.contestant_id == contestant_id).first()
    if request.method == "PATCH":
        dancer.guaranteed_entry = not dancer.guaranteed_entry
        db.session.commit()
    return jsonify(dancer.guaranteed_entry)
