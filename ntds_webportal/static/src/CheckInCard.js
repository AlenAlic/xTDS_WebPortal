var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var countCheckedIn = function countCheckedIn(obj) {
    return obj.status_info.checked_in;
};
var getFullName = function getFullName(obj) {
    return obj.full_name;
};

var CheckInCard = function (_React$Component) {
    _inherits(CheckInCard, _React$Component);

    function CheckInCard(props) {
        _classCallCheck(this, CheckInCard);

        var _this = _possibleConstructorReturn(this, (CheckInCard.__proto__ || Object.getPrototypeOf(CheckInCard)).call(this, props));

        _this.state = { dancers: _this.props.start_dancers };
        _this.checkInOnClick = _this.checkInOnClick.bind(_this);
        _this.paymentOnClick = _this.paymentOnClick.bind(_this);
        _this.merchandiseReceivedOnClick = _this.merchandiseReceivedOnClick.bind(_this);
        return _this;
    }
    //    getTeamConfirmedDancers() {
    //        fetch("/api/teams/"+this.props.team_id+"/confirmed_dancers", {method: "GET"})
    //        .then(response => response.json())
    //        .then(res => {this.setState({dancers: res})} )
    //    }


    _createClass(CheckInCard, [{
        key: "checkCancelledDancersMerchandise",
        value: function checkCancelledDancersMerchandise() {
            fetch("/api/teams/" + this.props.team_id + "/cancelled_dancers_with_merchandise", { method: "GET" }).then(function (response) {
                return response.json();
            }).then(function (res) {
                var myList = [];
                for (var i = 0; i < res.length; i++) {
                    myList.push(res[i].full_name);
                }
                res.length > 0 ? alert("Warning!\n\nThere are dancers that have ordered merchandise, but have cancelled their registration.\n\nThese are:\n" + myList.join('\n') + "\n\nPlease give the merchandise of those dancers to the team captain.") : null;
            });
        }
    }, {
        key: "alertCheckInIncomplete",
        value: function alertCheckInIncomplete(d, idx) {
            var _this2 = this;

            var incomplete = !d.payment_info.all_paid || !(d.merchandise_info.ordered_merchandise ? d.merchandise_info.merchandise_received ? true : false : true) || !(d.status_info.dancing_lead ? d.status_info.received_starting_number : true);
            if (incomplete) {
                if (d.status_info.checked_in) {
                    fetch("/api/contestants/" + d.contestant_id + "/status_info/checked_in", { method: "PATCH" }).then(function (response) {
                        return response.json();
                    }).then(function (res) {
                        var dan = _this2.state.dancers;
                        dan[idx] = res;
                        _this2.setState({ dancers: dan });
                    });
                } else {
                    alert("ATTENTION!\n\nCheck if the dancer has paid, received their merchandise, and has received his/her number.");
                }
            } else {
                fetch("/api/contestants/" + d.contestant_id + "/status_info/checked_in", { method: "PATCH" }).then(function (response) {
                    return response.json();
                }).then(function (res) {
                    var dan = _this2.state.dancers;
                    dan[idx] = res;
                    _this2.setState({ dancers: dan });
                    res.contestant_info.team_captain && res.status_info.checked_in ? _this2.checkCancelledDancersMerchandise() : null;
                });
            }
        }
    }, {
        key: "checkInOnClick",
        value: function checkInOnClick(id, idx) {
            var _this3 = this;

            fetch("/api/contestants/" + id, { method: "GET" }).then(function (response) {
                return response.json();
            }).then(function (res) {
                _this3.alertCheckInIncomplete(res, idx);
            });
        }
    }, {
        key: "paymentOnClick",
        value: function paymentOnClick(id, idx) {
            var _this4 = this;

            fetch("/api/contestants/" + id + "/payment_info/all_paid", { method: "PATCH" }).then(function (response) {
                return response.json();
            }).then(function (res) {
                var dan = _this4.state.dancers;
                dan[idx] = res;
                _this4.setState({ dancers: dan });
            });
        }
    }, {
        key: "merchandiseReceivedOnClick",
        value: function merchandiseReceivedOnClick(id, idx) {
            var _this5 = this;

            fetch("/api/contestants/" + id + "/merchandise_info/merchandise_received", { method: "PATCH" }).then(function (response) {
                return response.json();
            }).then(function (res) {
                var dan = _this5.state.dancers;
                dan[idx] = res;
                _this5.setState({ dancers: dan });
            });
        }
    }, {
        key: "receivedNumberOnClick",
        value: function receivedNumberOnClick(id, idx) {
            var _this6 = this;

            fetch("/api/contestants/" + id + "/status_info/received_starting_number", { method: "PATCH" }).then(function (response) {
                return response.json();
            }).then(function (res) {
                var dan = _this6.state.dancers;
                dan[idx] = res;
                _this6.setState({ dancers: dan });
            });
        }
    }, {
        key: "render",
        value: function render() {
            var _this7 = this;

            return React.createElement(
                "div",
                { className: this.state.dancers.filter(countCheckedIn).length == this.state.dancers.length ? "card success" : "card", id: "render-team-card-{{team['team_id']}}" },
                React.createElement(
                    "div",
                    { className: "card-header", role: "button", id: 'heading-' + ("" + this.props.team_id), "data-toggle": "collapse", href: '#collapse-' + ("" + this.props.team_id), "aria-expanded": "false", "aria-controls": 'collapse-' + ("" + this.props.team_id) },
                    React.createElement(
                        "b",
                        { className: "card-title" },
                        this.props.teamName,
                        " ",
                        React.createElement(
                            "span",
                            { className: "badge badge-pill badge-dark" },
                            " ",
                            this.state.dancers.filter(countCheckedIn).length,
                            " / ",
                            this.state.dancers.length
                        )
                    )
                ),
                React.createElement(
                    "div",
                    { id: 'collapse-' + ("" + this.props.team_id), className: "collapse", role: "tabpanel", "aria-labelledby": 'heading-' + ("" + this.props.team_id) },
                    React.createElement(
                        "table",
                        { className: "table table-sm table-hover mb-0" },
                        React.createElement(
                            "colgroup",
                            null,
                            React.createElement("col", { span: "1", style: { width: '15%' } }),
                            React.createElement("col", { span: "1", style: { width: '10%' } }),
                            React.createElement("col", { span: "1", style: { width: '15%' } }),
                            React.createElement("col", { span: "1", style: { width: '10%' } }),
                            React.createElement("col", { span: "1", style: { width: '15%' } }),
                            React.createElement("col", { span: "1", style: { width: '5%' } }),
                            React.createElement("col", { span: "1", style: { width: '15%' } }),
                            React.createElement("col", { span: "1", style: { width: '15%' } })
                        ),
                        React.createElement(
                            "thead",
                            null,
                            React.createElement(
                                "tr",
                                null,
                                React.createElement("th", { colSpan: "2" }),
                                React.createElement(
                                    "th",
                                    null,
                                    "Finances"
                                ),
                                React.createElement(
                                    "th",
                                    { colSpan: "2" },
                                    "Merchandise"
                                ),
                                React.createElement("th", { colSpan: "4" })
                            ),
                            React.createElement(
                                "tr",
                                null,
                                React.createElement(
                                    "th",
                                    null,
                                    "Name"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Student"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Paid"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Ordered"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Received"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "#"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Received"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Checked in"
                                )
                            )
                        ),
                        React.createElement(
                            "tbody",
                            null,
                            this.state.dancers.map(function (d, idx) {
                                return React.createElement(
                                    "tr",
                                    { className: d.status_info.checked_in && d.payment_info.all_paid && (d.merchandise_info.ordered_merchandise ? d.merchandise_info.merchandise_received ? true : false : true) && (d.status_info.dancing_lead ? d.status_info.received_starting_number : true) ? 'table-success' : null, key: 'tr' + ("" + d.contestant_id) },
                                    React.createElement(
                                        "td",
                                        { key: 'td_name' + ("" + d.contestant_id) },
                                        d.full_name,
                                        d.contestant_info.team_captain ? ' - TC' : null
                                    ),
                                    React.createElement(
                                        "td",
                                        { key: 'td_student' + ("" + d.contestant_id) },
                                        d.contestant_info.student == "student" ? "Yes" : d.contestant_info.student == "non-student" ? "No" : "PhD student"
                                    ),
                                    React.createElement(
                                        "td",
                                        { key: 'td_paid_button' + ("" + d.contestant_id) },
                                        d.payment_info.all_paid ? React.createElement(Icon, { variant: "check" }) : React.createElement(Icon, { variant: "x" }),
                                        React.createElement(Button, { size: "sm", className: "ml-2", onClick: function onClick() {
                                                return _this7.paymentOnClick(d.contestant_id, idx);
                                            }, key: 'paid_button' + ("" + d.contestant_id), variant: "outline-dark", id: d.contestant_id, text: d.payment_info.all_paid ? 'Cancel payment' : 'Confirm payment' })
                                    ),
                                    React.createElement(
                                        "td",
                                        { key: 'td_merchandise_ordered' + ("" + d.contestant_id) },
                                        d.merchandise_info.ordered_merchandise ? "Yes:\xA0" : null,
                                        "d.merchandise_info.t_shirt" == "No" ? "👕" : null,
                                        d.merchandise_info.mug ? "🍺" : null,
                                        d.merchandise_info.bag ? "👜" : null
                                    ),
                                    React.createElement(
                                        "td",
                                        { key: 'td_merchandise_button' + ("" + d.contestant_id) },
                                        d.merchandise_info.ordered_merchandise ? d.merchandise_info.merchandise_received ? React.createElement(Icon, { variant: "check" }) : React.createElement(Icon, { variant: "x" }) : null,
                                        d.merchandise_info.ordered_merchandise ? React.createElement(Button, { size: "sm", className: "ml-2", onClick: function onClick() {
                                                return _this7.merchandiseReceivedOnClick(d.contestant_id, idx);
                                            }, key: 'merchandise_button' + ("" + d.contestant_id), variant: "outline-dark", id: d.contestant_id, text: d.merchandise_info.merchandise_received ? 'Withdraw merch' : 'Give merch' }) : null
                                    ),
                                    React.createElement(
                                        "td",
                                        { key: 'td_number' + ("" + d.contestant_id) },
                                        d.status_info.dancing_lead ? d.contestant_info.number : null
                                    ),
                                    React.createElement(
                                        "td",
                                        { key: 'td_number_button' + ("" + d.contestant_id) },
                                        d.status_info.dancing_lead ? d.status_info.received_starting_number ? React.createElement(Icon, { variant: "check" }) : React.createElement(Icon, { variant: "x" }) : null,
                                        d.status_info.dancing_lead ? React.createElement(Button, { size: "sm", className: "ml-2", onClick: function onClick() {
                                                return _this7.receivedNumberOnClick(d.contestant_id, idx);
                                            }, key: 'number_button' + ("" + d.contestant_id), variant: "outline-dark", id: d.contestant_id, text: d.status_info.received_starting_number ? 'Take number' : 'Give number' }) : null
                                    ),
                                    React.createElement(
                                        "td",
                                        { key: 'td_check_in_button' + ("" + d.contestant_id) },
                                        d.status_info.checked_in ? React.createElement(Icon, { variant: "check" }) : React.createElement(Icon, { variant: "x" }),
                                        React.createElement(Button, { size: "sm", className: "ml-2", onClick: function onClick() {
                                                return _this7.checkInOnClick(d.contestant_id, idx);
                                            }, key: 'check_in_button' + ("" + d.contestant_id), variant: "outline-dark", id: d.contestant_id, text: d.status_info.checked_in ? 'Check out' : 'Check in' })
                                    )
                                );
                            })
                        )
                    )
                )
            );
        }
    }]);

    return CheckInCard;
}(React.Component);