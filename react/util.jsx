// Dancer filters
const filterStudents = dancer => {return dancer.contestant_info.student === "student"};
const filterNonStudents = dancer => {return dancer.contestant_info.student === "non-student"};
const filterPhDStudents = dancer => {return dancer.contestant_info.student === "phd-student"};
const filterConfirmed = dancer => {return dancer.status_info.status === "confirmed"};
const filterCancelled = dancer => {return dancer.status_info.status === "cancelled"};
const filterEntryPaid = dancer => {return dancer.payment_info.entry_paid};
const filterEntryNotPaid = dancer => {return !dancer.payment_info.entry_paid};
const filterHasRefund = dancer => {return dancer.payment_info.refund};
const filterDoesNotHaveRefund = dancer => {return !dancer.payment_info.refund};
const filterHasMerchandise = dancer => {return Object.keys(dancer.merchandise_info.purchases).length > 0};
const filterAllPaid = dancer => {return dancer.payment_info.all_paid};
const filterPaymentRequired = dancer => {return dancer.status_info.payment_required};

// Dancer mappings
const mapEntryPrice = dancer => dancer.payment_info.entry_price;
const mapMerchandisePrice = dancer => dancer.merchandise_info.merchandise_price;
const mapPaymentPrice = dancer => dancer.payment_info.payment_price;
const mapRefundPrice = dancer => dancer.payment_info.refund_price;

// Sum array
const reduceArraySum = (prev, next) => {return prev + next};

const countStudents = dancer => {return dancer.contestant_info.student === "student"};
const countNonStudents = dancer => {return dancer.contestant_info.student === "non-student"};
const countPhDStudents = dancer => {return dancer.contestant_info.student === "phd-student"};
const countEntryPaid = dancer => {return dancer.payment_info.entry_paid};
const countEntryNotPaid = dancer => {return !dancer.payment_info.entry_paid};
const confirmed = dancer => {return dancer.status_info.status === "confirmed"};
const cancelled = dancer => {return dancer.status_info.status === "cancelled"};
const hasRefund = dancer => {return dancer.payment_info.refund};
const hasMerchandise = dancer => {return Object.keys(dancer.merchandise_info.purchases).length > 0};
const hasMerchandisePaid = merchandise => {return merchandise.paid};
const arrSum = arr => arr.reduce((a,b) => a + b, 0);
const sortDancersAlphabetically = (a, b) => {
    let nameA = a.full_name.toUpperCase();
    let nameB = b.full_name.toUpperCase();
    if (nameA < nameB) {return -1;}
    if (nameA > nameB) {return 1;}
    return 0;
};
const sortMerchandiseAlphabetically = (a, b) => {
    let nameA = a.description.toUpperCase();
    let nameB = b.description.toUpperCase();
    if (nameA < nameB) {return -1;}
    if (nameA > nameB) {return 1;}
    return 0;
};
const currencyFormat = num => {
    let sign = num >= 0 ? '€' : '-€';
    num = Math.abs(num);
    if (num !== 0) {
        num = num / 100;
        return sign + num.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
    } else {
        return '-'
    }
};


const countCheckedIn = dancer => {return dancer.status_info.checked_in};
const countSpecialCheckedIn = dancer => {return dancer.payment_info.all_paid && dancer.merchandise_info.merchandise_received && dancer.status_info.status === "cancelled" || dancer.status_info.checked_in};

const countLeads = dancer => {return dancer.status_info.dancing_lead};
const countStartingNumbers = dancer => {return dancer.status_info.received_starting_number};
const countReceivedMerchandise = dancer => {return dancer.merchandise_info.merchandise_received};

const CheckMark = ({flag}) => {
    return flag ? <i className="fas fa-check"/>: <i className="fas fa-times"/>;
};


const countDutchTeams = team => {return team.country === "The Netherlands"};
const countGermanTeams = team => {return team.country === "Germany"};
const countOtherTeams = team => {return team.country !== "The Netherlands" && team.country !== "Germany"};
const countTeamsWithDancers = team => {return Object.values(team.finances_data.dancers).length > 0};
const sortTeamsAlphabetically = (a, b) => {
    let nameA = a.name.toUpperCase();
    let nameB = b.name.toUpperCase();
    if (nameA < nameB) {return -1;}
    if (nameA > nameB) {return 1;}
    return 0;
};
const countAllPaid = dancer => {return dancer.payment_info.all_paid};
const countAllNotPaid = dancer => {return !dancer.payment_info.all_paid};