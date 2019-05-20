// Dancer filters
var filterStudents = function filterStudents(dancer) {
    return dancer.contestant_info.student === "student";
};
var filterNonStudents = function filterNonStudents(dancer) {
    return dancer.contestant_info.student === "non-student";
};
var filterPhDStudents = function filterPhDStudents(dancer) {
    return dancer.contestant_info.student === "phd-student";
};
var filterConfirmed = function filterConfirmed(dancer) {
    return dancer.status_info.status === "confirmed";
};
var filterCancelled = function filterCancelled(dancer) {
    return dancer.status_info.status === "cancelled";
};
var filterEntryPaid = function filterEntryPaid(dancer) {
    return dancer.payment_info.entry_paid;
};
var filterEntryNotPaid = function filterEntryNotPaid(dancer) {
    return !dancer.payment_info.entry_paid;
};
var filterHasRefund = function filterHasRefund(dancer) {
    return dancer.payment_info.refund;
};
var filterDoesNotHaveRefund = function filterDoesNotHaveRefund(dancer) {
    return !dancer.payment_info.refund;
};
var filterHasMerchandise = function filterHasMerchandise(dancer) {
    return Object.keys(dancer.merchandise_info.purchases).length > 0;
};
var filterAllPaid = function filterAllPaid(dancer) {
    return dancer.payment_info.all_paid;
};
var filterPaymentRequired = function filterPaymentRequired(dancer) {
    return dancer.status_info.payment_required;
};

// Dancer mappings
var mapEntryPrice = function mapEntryPrice(dancer) {
    return dancer.payment_info.entry_price;
};
var mapMerchandisePrice = function mapMerchandisePrice(dancer) {
    return dancer.merchandise_info.merchandise_price;
};
var mapPaymentPrice = function mapPaymentPrice(dancer) {
    return dancer.payment_info.payment_price;
};
var mapRefundPrice = function mapRefundPrice(dancer) {
    return dancer.payment_info.refund_price;
};

// Sum array
var reduceArraySum = function reduceArraySum(prev, next) {
    return prev + next;
};

var countStudents = function countStudents(dancer) {
    return dancer.contestant_info.student === "student";
};
var countNonStudents = function countNonStudents(dancer) {
    return dancer.contestant_info.student === "non-student";
};
var countPhDStudents = function countPhDStudents(dancer) {
    return dancer.contestant_info.student === "phd-student";
};
var countEntryPaid = function countEntryPaid(dancer) {
    return dancer.payment_info.entry_paid;
};
var countEntryNotPaid = function countEntryNotPaid(dancer) {
    return !dancer.payment_info.entry_paid;
};
var confirmed = function confirmed(dancer) {
    return dancer.status_info.status === "confirmed";
};
var cancelled = function cancelled(dancer) {
    return dancer.status_info.status === "cancelled";
};
var hasRefund = function hasRefund(dancer) {
    return dancer.payment_info.refund;
};
var hasMerchandise = function hasMerchandise(dancer) {
    return Object.keys(dancer.merchandise_info.purchases).length > 0;
};
var hasMerchandisePaid = function hasMerchandisePaid(merchandise) {
    return merchandise.paid;
};
var arrSum = function arrSum(arr) {
    return arr.reduce(function (a, b) {
        return a + b;
    }, 0);
};
var sortDancersAlphabetically = function sortDancersAlphabetically(a, b) {
    var nameA = a.full_name.toUpperCase();
    var nameB = b.full_name.toUpperCase();
    if (nameA < nameB) {
        return -1;
    }
    if (nameA > nameB) {
        return 1;
    }
    return 0;
};
var sortMerchandiseAlphabetically = function sortMerchandiseAlphabetically(a, b) {
    var nameA = a.description.toUpperCase();
    var nameB = b.description.toUpperCase();
    if (nameA < nameB) {
        return -1;
    }
    if (nameA > nameB) {
        return 1;
    }
    return 0;
};
var currencyFormat = function currencyFormat(num) {
    var sign = num >= 0 ? '€' : '-€';
    num = Math.abs(num);
    if (num !== 0) {
        num = num / 100;
        return sign + num.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
    } else {
        return '-';
    }
};

var countCheckedIn = function countCheckedIn(dancer) {
    return dancer.status_info.checked_in;
};
var countSpecialCheckedIn = function countSpecialCheckedIn(dancer) {
    return dancer.payment_info.all_paid && dancer.merchandise_info.merchandise_received && dancer.status_info.status === "cancelled" || dancer.status_info.checked_in;
};

var countLeads = function countLeads(dancer) {
    return dancer.status_info.dancing_lead;
};
var countStartingNumbers = function countStartingNumbers(dancer) {
    return dancer.status_info.received_starting_number;
};
var countReceivedMerchandise = function countReceivedMerchandise(dancer) {
    return dancer.merchandise_info.merchandise_received;
};

var CheckMark = function CheckMark(_ref) {
    var flag = _ref.flag;

    return flag ? React.createElement("i", { className: "fas fa-check" }) : React.createElement("i", { className: "fas fa-times" });
};

var countDutchTeams = function countDutchTeams(team) {
    return team.country === "The Netherlands";
};
var countGermanTeams = function countGermanTeams(team) {
    return team.country === "Germany";
};
var countOtherTeams = function countOtherTeams(team) {
    return team.country !== "The Netherlands" && team.country !== "Germany";
};
var countTeamsWithDancers = function countTeamsWithDancers(team) {
    return Object.values(team.finances_data.dancers).length > 0;
};
var sortTeamsAlphabetically = function sortTeamsAlphabetically(a, b) {
    var nameA = a.name.toUpperCase();
    var nameB = b.name.toUpperCase();
    if (nameA < nameB) {
        return -1;
    }
    if (nameA > nameB) {
        return 1;
    }
    return 0;
};
var countAllPaid = function countAllPaid(dancer) {
    return dancer.payment_info.all_paid;
};
var countAllNotPaid = function countAllNotPaid(dancer) {
    return !dancer.payment_info.all_paid;
};