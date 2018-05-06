from ntds_webportal import db
from ntds_webportal.models import Contestant, ContestantInfo, DancingInfo, StatusInfo
import ntds_webportal.data as data

# Load Settings

# Load values
all_dancers = db.session.query(Contestant).join(ContestantInfo).join(StatusInfo)\
    .filter(StatusInfo.status != data.CANCELLED).all()
registered_dancers = [dancer for dancer in all_dancers if dancer.status_info[0].status == data.REGISTERED]
selected_dancers = [dancer for dancer in all_dancers if dancer.status_info[0].status == data.SELECTED]
confirmed_dancers = [dancer for dancer in all_dancers if dancer.status_info[0].status == data.CONFIRMED]


# Select teamcaptains

# Select rest

