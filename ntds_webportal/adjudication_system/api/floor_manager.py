from flask import jsonify, request
from flask_login import login_required
from ntds_webportal import db
from ntds_webportal.models import CouplePresent, requires_access_level
from ntds_webportal.adjudication_system.api import bp
from ntds_webportal.data import *


@bp.route('/present/<int:present_id>/present', methods=["GET", "PATCH"])
@login_required
@requires_access_level([ACCESS[FLOOR_MANAGER]])
def present_present(present_id):
    present = CouplePresent.query.get_or_404(present_id)
    if request.method == "PATCH":
        present.present = not present.present
        db.session.commit()
    return jsonify(present.present)
