var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var TournamentCheckin = function (_React$Component) {
    _inherits(TournamentCheckin, _React$Component);

    function TournamentCheckin(props) {
        _classCallCheck(this, TournamentCheckin);

        var _this = _possibleConstructorReturn(this, (TournamentCheckin.__proto__ || Object.getPrototypeOf(TournamentCheckin)).call(this, props));

        _this.state = { dancers: _this.props.dancers };
        return _this;
    }

    _createClass(TournamentCheckin, [{
        key: "render",
        value: function render() {
            var dancers = Object.values(this.state.dancers);
            var confirmedDancers = dancers.filter(filterConfirmed);
            var checkedInDancers = confirmedDancers.filter(filterCheckedIn);
            var confirmedLeads = confirmedDancers.filter(filterLeads);
            var receivedStartingNumber = confirmedLeads.filter(filterStartingNumbers);
            var cancelledDancers = dancers.filter(filterCancelled);
            var cancelledDancersReceivedMerchandise = cancelledDancers.filter(filterReceivedMerchandise);

            return React.createElement(
                React.Fragment,
                null,
                React.createElement(
                    "b",
                    { className: "d-block my-2 mt-3" },
                    "Checked in ",
                    React.createElement(
                        "span",
                        { className: "badge badge-pill badge-dark" },
                        checkedInDancers.length,
                        " / ",
                        confirmedDancers.length
                    )
                ),
                React.createElement(
                    "b",
                    { className: "d-block my-2" },
                    "Received starting number ",
                    React.createElement(
                        "span",
                        { className: "badge badge-pill badge-dark" },
                        receivedStartingNumber.length,
                        " / ",
                        confirmedLeads.length
                    )
                ),
                React.createElement(
                    "table",
                    { className: "table table-sm mb-5" },
                    React.createElement(
                        "thead",
                        null,
                        React.createElement(
                            "tr",
                            null,
                            React.createElement("th", { colSpan: "2" }),
                            React.createElement(
                                "th",
                                { colSpan: "3" },
                                "Merchandise"
                            ),
                            React.createElement("th", { colSpan: "2" })
                        ),
                        React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "th",
                                { style: { width: '25%' } },
                                "Dancer"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' } },
                                "Paid entry fee"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '25%' } },
                                "Ordered"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' } },
                                "Paid"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' } },
                                "Received"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' } },
                                "Checked in"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' } },
                                "Got number"
                            )
                        )
                    ),
                    React.createElement(
                        "tbody",
                        null,
                        confirmedDancers.sort(sortDancersAlphabetically).map(function (d) {
                            return React.createElement(
                                "tr",
                                { className: d.payment_info.all_paid && d.merchandise_info.merchandise_received && d.status_info.checked_in ? d.status_info.received_starting_number ? 'table-success' : 'table-primary' : null, key: 'row' + ("" + d.contestant_id) },
                                React.createElement(
                                    "td",
                                    null,
                                    d.full_name
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(CheckMark, { flag: d.payment_info.entry_paid })
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    d.merchandise_info.merchandise_ordered ? React.createElement(CheckMark, { flag: d.merchandise_info.merchandise_ordered }) : null
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    d.merchandise_info.merchandise_ordered ? React.createElement(CheckMark, { flag: d.merchandise_info.merchandise_paid }) : null
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    d.merchandise_info.merchandise_ordered ? React.createElement(CheckMark, { flag: d.merchandise_info.merchandise_received }) : null
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(CheckMark, { flag: d.status_info.checked_in })
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(CheckMark, { flag: d.status_info.received_starting_number })
                                )
                            );
                        }),
                        cancelledDancers.length > 0 ? React.createElement(
                            React.Fragment,
                            null,
                            React.createElement(
                                "tr",
                                null,
                                React.createElement(
                                    "th",
                                    { colSpan: "7", className: "pt-5" },
                                    "Cancelled dancers with ordered merchandise ",
                                    React.createElement(
                                        "span",
                                        { className: "badge badge-pill badge-dark" },
                                        cancelledDancersReceivedMerchandise.length,
                                        " / ",
                                        cancelledDancers.length
                                    )
                                )
                            ),
                            React.createElement(
                                "tr",
                                null,
                                React.createElement("th", { colSpan: "2" }),
                                React.createElement(
                                    "th",
                                    { colSpan: "3" },
                                    "Merchandise"
                                ),
                                React.createElement("th", { colSpan: "2" })
                            ),
                            React.createElement(
                                "tr",
                                null,
                                React.createElement(
                                    "th",
                                    null,
                                    "Dancer"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Paid entry fee"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Ordered"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Paid"
                                ),
                                React.createElement(
                                    "th",
                                    null,
                                    "Received"
                                ),
                                React.createElement("th", { colSpan: "2" })
                            ),
                            cancelledDancers.sort(sortDancersAlphabetically).map(function (d) {
                                return React.createElement(
                                    "tr",
                                    { className: d.payment_info.all_paid && d.merchandise_info.merchandise_received ? 'table-success' : null, key: 'row' + ("" + d.contestant_id) },
                                    React.createElement(
                                        "td",
                                        null,
                                        d.full_name
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        React.createElement(CheckMark, { flag: d.payment_info.entry_paid })
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(function (p) {
                                            return React.createElement(
                                                "div",
                                                { key: 'item' + ("" + p.merchandise_purchased_id) },
                                                p.item
                                            );
                                        }) : "-"
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(function (p) {
                                            return React.createElement(
                                                "div",
                                                { key: 'price' + ("" + p.merchandise_purchased_id) },
                                                React.createElement(CheckMark, { flag: p.paid })
                                            );
                                        }) : "-"
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(function (p) {
                                            return React.createElement(
                                                "div",
                                                { key: 'paid' + ("" + p.merchandise_purchased_id) },
                                                React.createElement(CheckMark, { flag: p.received })
                                            );
                                        }) : "-"
                                    ),
                                    React.createElement("td", null),
                                    React.createElement("td", null)
                                );
                            })
                        ) : null
                    )
                )
            );
        }
    }]);

    return TournamentCheckin;
}(React.Component);