var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var CheckinCard = function (_React$Component) {
    _inherits(CheckinCard, _React$Component);

    function CheckinCard(props) {
        _classCallCheck(this, CheckinCard);

        var _this = _possibleConstructorReturn(this, (CheckinCard.__proto__ || Object.getPrototypeOf(CheckinCard)).call(this, props));

        _this.state = { dancers: {} };
        _this.setPending = _this.setPending.bind(_this);
        _this.entryPayment = _this.entryPayment.bind(_this);
        _this.merchandisePayment = _this.merchandisePayment.bind(_this);
        _this.merchandiseReceived = _this.merchandiseReceived.bind(_this);
        _this.tryCheckIn = _this.tryCheckIn.bind(_this);
        _this.checkIn = _this.checkIn.bind(_this);
        return _this;
    }

    _createClass(CheckinCard, [{
        key: "componentDidMount",
        value: function componentDidMount() {
            this.getTeamDancers();
        }
    }, {
        key: "getTeamDancers",
        value: function getTeamDancers() {
            var _this2 = this;

            fetch("/api/teams/" + this.props.team_id + "/check_in_dancers", { method: "GET", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                _this2.setState({ dancers: result });
            });
        }
    }, {
        key: "setPending",
        value: function setPending(dancer) {
            var newState = this.state.dancers;
            dancer.pending = true;
            newState[dancer.contestant_id] = dancer;
            this.setState({ dancers: newState });
        }
    }, {
        key: "entryPayment",
        value: function entryPayment(dancer) {
            var _this3 = this;

            this.setPending(dancer);
            var newState = this.state.dancers;
            fetch("/api/contestants/" + dancer.contestant_id + "/entry_payment/" + Number(!dancer.payment_info.entry_paid), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                newState[result.contestant_id] = result;
                _this3.setState({ dancers: newState });
            }).catch(function (error) {
                console.log('Error: \n', error);
                dancer.pending = false;
                newState[dancer.contestant_id] = dancer;
                _this3.setState({ dancers: newState });
            });
        }
    }, {
        key: "merchandisePayment",
        value: function merchandisePayment(dancer, purchase) {
            var _this4 = this;

            this.setPending(dancer);
            var newState = this.state.dancers;
            fetch("/api/contestants/" + dancer.contestant_id + "/merchandise_payment/" + purchase.merchandise_purchased_id + "/" + Number(!purchase.paid), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                newState[result.contestant_id] = result;
                _this4.setState({ dancers: newState });
            }).catch(function (error) {
                console.log('Error: \n', error);
                dancer.pending = false;
                newState[dancer.contestant_id] = dancer;
                _this4.setState({ dancers: newState });
            });
        }
    }, {
        key: "merchandiseReceived",
        value: function merchandiseReceived(dancer, purchase) {
            var _this5 = this;

            this.setPending(dancer);
            var newState = this.state.dancers;
            fetch("/api/contestants/" + dancer.contestant_id + "/merchandise_received/" + purchase.merchandise_purchased_id + "/" + Number(!purchase.received), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                newState[result.contestant_id] = result;
                _this5.setState({ dancers: newState });
            }).catch(function (error) {
                console.log('Error: \n', error);
                dancer.pending = false;
                newState[dancer.contestant_id] = dancer;
                _this5.setState({ dancers: newState });
            });
        }
    }, {
        key: "tryCheckIn",
        value: function tryCheckIn(dancer) {
            if (dancer.status_info.checked_in) {
                this.checkIn(dancer);
            } else {
                var complete = dancer.payment_info.all_paid && dancer.merchandise_info.merchandise_received;
                if (complete) {
                    if (dancer.contestant_info.team_captain) {
                        this.checkCancelledDancersMerchandise();
                    }
                    this.checkIn(dancer);
                } else {
                    if (dancer.merchandise_info.ordered_merchandise) {
                        alert("ATTENTION!\n\nCannot check in dancer.\n\nPlease check that the dancer has paid the entry fee, and has received and paid their merchandise.");
                    } else {
                        alert("ATTENTION!\n\nCannot check in dancer.\n\nPlease check that the dancer has paid the entry fee.");
                    }
                }
            }
        }
    }, {
        key: "checkIn",
        value: function checkIn(dancer) {
            var _this6 = this;

            this.setPending(dancer);
            var newState = this.state.dancers;
            fetch("/api/contestants/" + dancer.contestant_id + "/check_in/" + Number(!dancer.status_info.checked_in), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                newState[result.contestant_id] = result;
                _this6.setState({ dancers: newState });
            }).catch(function (error) {
                console.log('Error: \n', error);
                dancer.pending = false;
                newState[dancer.contestant_id] = dancer;
                _this6.setState({ dancers: newState });
            });
        }
    }, {
        key: "checkCancelledDancersMerchandise",
        value: function checkCancelledDancersMerchandise() {
            fetch("/api/teams/" + this.props.team_id + "/cancelled_dancers_with_merchandise", { method: "GET", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (res) {
                var myList = [];
                for (var i = 0; i < res.length; i++) {
                    myList.push(res[i].full_name);
                }
                res.length > 0 ? alert("ATTENTION!!\n\nThere are dancers that have ordered merchandise, but have cancelled their registration.\n\nThese are:\n" + myList.join('\n') + "\n\nPlease give the merchandise of those dancers to the team captain, and mark the merchandise as received in this list") : null;
            });
        }
    }, {
        key: "render",
        value: function render() {
            var _this7 = this;

            var dancers = Object.values(this.state.dancers);

            return React.createElement(
                "div",
                { className: dancers.length > 0 ? dancers.filter(filterCheckedIn).length === dancers.length ? "card success" : "card" : "card" },
                React.createElement(
                    "div",
                    { className: "card-header", role: "button", id: 'heading-' + ("" + this.props.team_id), "data-toggle": "collapse", href: '#collapse-' + ("" + this.props.team_id), "aria-expanded": "false", "aria-controls": 'collapse-' + ("" + this.props.team_id) },
                    React.createElement(
                        "b",
                        { className: "card-title" },
                        this.props.team_name,
                        " ",
                        dancers.length === 0 ? React.createElement("div", { className: "spinner-border spinner-border-sm", role: "status" }) : React.createElement(
                            "span",
                            { className: "badge badge-pill badge-dark" },
                            " ",
                            dancers.filter(filterSpecialCheckedIn).length,
                            " / ",
                            dancers.length
                        )
                    )
                ),
                React.createElement(
                    "div",
                    { id: 'collapse-' + ("" + this.props.team_id), className: "collapse" },
                    dancers.length === 0 ? null : React.createElement(
                        "table",
                        { className: "table table-hover table-sm mb-0" },
                        React.createElement(
                            "thead",
                            null,
                            React.createElement(
                                "tr",
                                null,
                                React.createElement("th", null),
                                React.createElement(
                                    "th",
                                    { colSpan: "3" },
                                    "Entry fee"
                                ),
                                React.createElement(
                                    "th",
                                    { colSpan: "3" },
                                    "Merchandise"
                                ),
                                React.createElement("th", null)
                            ),
                            React.createElement(
                                "tr",
                                null,
                                React.createElement(
                                    "th",
                                    { style: { width: '15%' } },
                                    "Name"
                                ),
                                React.createElement(
                                    "th",
                                    { style: { width: '10%' } },
                                    "Student"
                                ),
                                React.createElement(
                                    "th",
                                    { style: { width: '10%' } },
                                    "Fee"
                                ),
                                React.createElement(
                                    "th",
                                    { style: { width: '10%' } },
                                    "Paid"
                                ),
                                React.createElement(
                                    "th",
                                    { style: { width: '15%' } },
                                    "Ordered"
                                ),
                                React.createElement(
                                    "th",
                                    { style: { width: '15%' } },
                                    "Paid"
                                ),
                                React.createElement(
                                    "th",
                                    { style: { width: '15%' } },
                                    "Received"
                                ),
                                React.createElement(
                                    "th",
                                    { style: { width: '10%' } },
                                    "Checked in"
                                )
                            )
                        ),
                        React.createElement(
                            "tbody",
                            null,
                            dancers.sort(sortDancersAlphabetically).map(function (d) {
                                return Object.keys(d.merchandise_info.purchases).length === 0 ? React.createElement(
                                    "tr",
                                    { className: d.pending ? 'table-warning' : d.payment_info.all_paid && d.merchandise_info.merchandise_received ? d.status_info.checked_in && d.status_info.status === "confirmed" || d.status_info.status === "cancelled" ? 'table-success' : null : null, key: 'row' + ("" + d.contestant_id) },
                                    React.createElement(
                                        "td",
                                        null,
                                        d.full_name,
                                        d.contestant_info.team_captain ? ' - TC' : null
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        d.contestant_info.student === "student" ? "Yes" : d.contestant_info.student === "non-student" ? "No" : "PhD student"
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        currencyFormat(_this7.props.prices[d.contestant_info.student])
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        React.createElement(
                                            "button",
                                            { className: "btn " + (d.payment_info.entry_paid ? "btn-outline-secondary" : "btn-danger"), onClick: function onClick() {
                                                    return _this7.entryPayment(d);
                                                } },
                                            d.payment_info.entry_paid ? React.createElement("i", { className: "fas fa-check" }) : React.createElement("i", { className: "fas fa-times" })
                                        )
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        "-"
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        "-"
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        "-"
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        d.status_info.status === "confirmed" ? React.createElement(
                                            "button",
                                            { className: "btn " + (d.status_info.checked_in ? "btn-outline-secondary" : "btn-danger"), onClick: function onClick() {
                                                    return _this7.tryCheckIn(d);
                                                } },
                                            d.status_info.checked_in ? React.createElement("i", { className: "fas fa-check" }) : React.createElement("i", { className: "fas fa-times" })
                                        ) : null
                                    )
                                ) : Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(function (p, i) {
                                    return React.createElement(
                                        "tr",
                                        { className: d.pending ? 'table-warning' : d.payment_info.all_paid && d.merchandise_info.merchandise_received ? d.status_info.checked_in && d.status_info.status === "confirmed" || d.status_info.status === "cancelled" ? 'table-success' : null : null, key: 'row' + (d.contestant_id + "-" + p.merchandise_purchased_id) },
                                        i === 0 ? React.createElement(
                                            React.Fragment,
                                            null,
                                            React.createElement(
                                                "td",
                                                null,
                                                d.full_name,
                                                d.contestant_info.team_captain ? ' - TC' : null
                                            ),
                                            React.createElement(
                                                "td",
                                                null,
                                                d.contestant_info.student === "student" ? "Yes" : d.contestant_info.student === "non-student" ? "No" : "PhD student"
                                            ),
                                            React.createElement(
                                                "td",
                                                null,
                                                currencyFormat(_this7.props.prices[d.contestant_info.student])
                                            ),
                                            React.createElement(
                                                "td",
                                                null,
                                                React.createElement(
                                                    "button",
                                                    { className: "btn " + (d.payment_info.entry_paid ? "btn-outline-secondary" : "btn-danger"), onClick: function onClick() {
                                                            return _this7.entryPayment(d);
                                                        } },
                                                    d.payment_info.entry_paid ? React.createElement("i", { className: "fas fa-check" }) : React.createElement("i", { className: "fas fa-times" })
                                                )
                                            )
                                        ) : React.createElement("td", { className: "border-0", colSpan: "4" }),
                                        React.createElement(
                                            "td",
                                            { className: i === 0 ? "" : "border-0" },
                                            p.item,
                                            " (",
                                            currencyFormat(p.price),
                                            ")"
                                        ),
                                        React.createElement(
                                            "td",
                                            { className: i === 0 ? "" : "border-0" },
                                            React.createElement(
                                                "button",
                                                { className: "btn " + (p.paid ? "btn-outline-secondary" : "btn-danger"), onClick: function onClick() {
                                                        return _this7.merchandisePayment(d, p);
                                                    } },
                                                p.paid ? React.createElement("i", { className: "fas fa-check" }) : React.createElement("i", { className: "fas fa-times" }),
                                                " Paid"
                                            )
                                        ),
                                        React.createElement(
                                            "td",
                                            { className: i === 0 ? "" : "border-0" },
                                            React.createElement(
                                                "button",
                                                { className: "btn " + (p.received ? "btn-outline-secondary" : "btn-danger"), onClick: function onClick() {
                                                        return _this7.merchandiseReceived(d, p);
                                                    } },
                                                p.received ? React.createElement("i", { className: "fas fa-check" }) : React.createElement("i", { className: "fas fa-times" }),
                                                " Received"
                                            )
                                        ),
                                        i === 0 ? React.createElement(
                                            "td",
                                            null,
                                            d.status_info.status === "confirmed" ? React.createElement(
                                                "button",
                                                { className: "btn " + (d.status_info.checked_in ? "btn-outline-secondary" : "btn-danger"), onClick: function onClick() {
                                                        return _this7.tryCheckIn(d);
                                                    } },
                                                d.status_info.checked_in ? React.createElement("i", { className: "fas fa-check" }) : React.createElement("i", { className: "fas fa-times" })
                                            ) : null
                                        ) : React.createElement("td", { className: "border-0" })
                                    );
                                });
                            })
                        )
                    )
                )
            );
        }
    }]);

    return CheckinCard;
}(React.Component);