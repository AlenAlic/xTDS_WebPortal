// Filters
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
const filterCheckedIn = dancer => {return dancer.status_info.checked_in};
const filterSpecialCheckedIn = dancer => {return dancer.payment_info.all_paid && dancer.merchandise_info.merchandise_received && dancer.status_info.status === "cancelled" || dancer.status_info.checked_in};
const filterLeads = dancer => {return dancer.status_info.dancing_lead};
const filterStartingNumbers = dancer => {return dancer.status_info.received_starting_number};
const filterReceivedMerchandise = dancer => {return dancer.merchandise_info.merchandise_received};
const filterHasMerchandisePaid = merchandise => {return merchandise.paid};
const filterDutchTeams = team => {return team.country === "The Netherlands"};
const filterGermanTeams = team => {return team.country === "Germany"};
const filterOtherTeams = team => {return team.country !== "The Netherlands" && team.country !== "Germany"};
const filterTeamsWithDancers = team => {return Object.values(team.finances_data.dancers).length > 0};
const filterUserIsTeamcaptain = user => {return user.is_teamcaptain};
const filterUserActivate = user => {return user.activate};
const filterUserIsActive = user => {return user.is_active};
const filterUserIsNotActive = user => {return !user.is_active};
const filterUserIsTreasurer = user => {return user.is_treasurer};

// Mappings
const mapEntryPrice = dancer => dancer.payment_info.entry_price;
const mapMerchandisePrice = dancer => dancer.merchandise_info.merchandise_price;
const mapPaymentPrice = dancer => dancer.payment_info.payment_price;
const mapRefundPrice = dancer => dancer.payment_info.refund_price;

// Reducers
const reduceArraySum = (prev, next) => {return prev + next};

// Sum Array function
const arrSum = arr => arr.reduce((a,b) => a + b, 0);

// Sorts
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
const sortTeamsAlphabetically = (a, b) => {
    let nameA = a.name.toUpperCase();
    let nameB = b.name.toUpperCase();
    if (nameA < nameB) {return -1;}
    if (nameA > nameB) {return 1;}
    return 0;
};
const sortUsersByIsActive = (a, b) => {
    let activeA = a.is_active;
    let activeB = b.is_active;
    if (activeA && !activeB) {return -1;}
    if (!activeA && activeB) {return 1;}
    return 0;
};
const sortUsersByIsActiveTeamTeamcaptain = (a, b) => {
    let activeA = a.is_active;
    let activeB = b.is_active;
    if (activeA && !activeB) {return -1;}
    if (!activeA && activeB) {return 1;}

    let nameA = a.team.toUpperCase();
    let nameB = b.team.toUpperCase();
    if (nameA < nameB) {return -1;}
    if (nameA > nameB) {return 1;}

    let teamcaptainA = a.is_teamcaptain;
    let teamcaptainB = b.is_teamcaptain;
    if (teamcaptainA && !teamcaptainB) {return -1;}
    if (!teamcaptainA && teamcaptainB) {return 1;}
    return 0;
};

// Formatting
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


// General DOM elements
const CheckMark = ({flag}) => {
    return flag ? <i className="fas fa-check"/>: <i className="fas fa-times"/>;
};


// General functionz
const classNamesFilterString = item => {return typeof item === "string"};
const classNamesFilterObject = item => {return typeof item === "object"};
const classNamesFilterValidObject = item => {return Object.values(item).length === 1 && Object.keys(item).length === 1 && typeof Object.values(item)[0] === 'boolean'};
const classNamesFilterTrueObjects = item => {return Object.values(item)[0] === true};
const classNamesMapObjects = item => Object.keys(item);
const classNames = (...names) => {
    let strings = names.filter(classNamesFilterString);
    let objectStrings = names.filter(classNamesFilterObject).filter(classNamesFilterValidObject).filter(classNamesFilterTrueObjects).map(classNamesMapObjects);
    return strings.concat(objectStrings).join(" ");
};

const validateEmail = email => {
    let re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
};