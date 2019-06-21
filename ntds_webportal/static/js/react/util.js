var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

// Filters
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
var filterCheckedIn = function filterCheckedIn(dancer) {
    return dancer.status_info.checked_in;
};
var filterSpecialCheckedIn = function filterSpecialCheckedIn(dancer) {
    return dancer.payment_info.all_paid && dancer.merchandise_info.merchandise_received && dancer.status_info.status === "cancelled" || dancer.status_info.checked_in;
};
var filterLeads = function filterLeads(dancer) {
    return dancer.status_info.dancing_lead;
};
var filterStartingNumbers = function filterStartingNumbers(dancer) {
    return dancer.status_info.received_starting_number;
};
var filterReceivedMerchandise = function filterReceivedMerchandise(dancer) {
    return dancer.merchandise_info.merchandise_received;
};
var filterHasMerchandisePaid = function filterHasMerchandisePaid(merchandise) {
    return merchandise.paid;
};
var filterDutchTeams = function filterDutchTeams(team) {
    return team.country === "The Netherlands";
};
var filterGermanTeams = function filterGermanTeams(team) {
    return team.country === "Germany";
};
var filterOtherTeams = function filterOtherTeams(team) {
    return team.country !== "The Netherlands" && team.country !== "Germany";
};
var filterTeamsWithDancers = function filterTeamsWithDancers(team) {
    return Object.values(team.finances_data.dancers).length > 0;
};
var filterUserIsTeamcaptain = function filterUserIsTeamcaptain(user) {
    return user.is_teamcaptain;
};
var filterUserActivate = function filterUserActivate(user) {
    return user.activate;
};
var filterUserIsActive = function filterUserIsActive(user) {
    return user.is_active;
};
var filterUserIsNotActive = function filterUserIsNotActive(user) {
    return !user.is_active;
};
var filterUserIsTreasurer = function filterUserIsTreasurer(user) {
    return user.is_treasurer;
};
var filterPurchaseNotCancelled = function filterPurchaseNotCancelled(purchase) {
    return !purchase.cancelled;
};

// Mappings
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

// Reducers
var reduceArraySum = function reduceArraySum(prev, next) {
    return prev + next;
};

// Sum Array function
var arrSum = function arrSum(arr) {
    return arr.reduce(function (a, b) {
        return a + b;
    }, 0);
};

// Sorts
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
var sortUsersByIsActive = function sortUsersByIsActive(a, b) {
    var activeA = a.is_active;
    var activeB = b.is_active;
    if (activeA && !activeB) {
        return -1;
    }
    if (!activeA && activeB) {
        return 1;
    }
    return 0;
};
var sortUsersByIsActiveTeamTeamcaptain = function sortUsersByIsActiveTeamTeamcaptain(a, b) {
    var activeA = a.is_active;
    var activeB = b.is_active;
    if (activeA && !activeB) {
        return -1;
    }
    if (!activeA && activeB) {
        return 1;
    }

    var nameA = a.team.toUpperCase();
    var nameB = b.team.toUpperCase();
    if (nameA < nameB) {
        return -1;
    }
    if (nameA > nameB) {
        return 1;
    }

    var teamcaptainA = a.is_teamcaptain;
    var teamcaptainB = b.is_teamcaptain;
    if (teamcaptainA && !teamcaptainB) {
        return -1;
    }
    if (!teamcaptainA && teamcaptainB) {
        return 1;
    }
    return 0;
};

// Formatting
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

// General DOM elements
var CheckMark = function CheckMark(_ref) {
    var flag = _ref.flag;

    return flag ? React.createElement("i", { className: "fas fa-check" }) : React.createElement("i", { className: "fas fa-times" });
};
var Toggle = function Toggle(_ref2) {
    var flag = _ref2.flag;

    return flag ? React.createElement("i", { className: "fas fa-toggle-on" }) : React.createElement("i", { className: "fas fa-toggle-off" });
};

// General functionz
var classNamesFilterString = function classNamesFilterString(item) {
    return typeof item === "string";
};
var classNamesFilterObject = function classNamesFilterObject(item) {
    return (typeof item === "undefined" ? "undefined" : _typeof(item)) === "object";
};
var classNamesFilterValidObject = function classNamesFilterValidObject(item) {
    return Object.values(item).length === 1 && Object.keys(item).length === 1 && typeof Object.values(item)[0] === 'boolean';
};
var classNamesFilterTrueObjects = function classNamesFilterTrueObjects(item) {
    return Object.values(item)[0] === true;
};
var classNamesMapObjects = function classNamesMapObjects(item) {
    return Object.keys(item);
};
var classNames = function classNames() {
    for (var _len = arguments.length, names = Array(_len), _key = 0; _key < _len; _key++) {
        names[_key] = arguments[_key];
    }

    var strings = names.filter(classNamesFilterString);
    var objectStrings = names.filter(classNamesFilterObject).filter(classNamesFilterValidObject).filter(classNamesFilterTrueObjects).map(classNamesMapObjects);
    return strings.concat(objectStrings).join(" ");
};

var validateEmail = function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
};