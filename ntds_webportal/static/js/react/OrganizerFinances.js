var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var OrganizerFinancesDropDown = function OrganizerFinancesDropDown(_ref) {
    var teams = _ref.teams,
        text = _ref.text;

    return React.createElement(
        "li",
        { className: "nav-item dropdown" },
        React.createElement(
            "a",
            { className: "nav-link dropdown-toggle", "data-toggle": "dropdown", "data-display": "static", href: "#", role: "button" },
            text,
            " teams"
        ),
        React.createElement(
            "div",
            { className: "dropdown-menu" },
            teams.sort(sortTeamsAlphabetically).map(function (t) {
                return React.createElement(
                    "a",
                    { className: "dropdown-item", id: "team-" + t.team_id, href: "#tab-" + t.team_id, key: "team-" + t.team_id, "data-toggle": "tab", role: "tab" },
                    t.name,
                    " ",
                    React.createElement(
                        "span",
                        { className: "badge badge-pill badge-dark" },
                        Object.values(t.finances_data.dancers).filter(filterAllPaid).length,
                        " / ",
                        Object.values(t.finances_data.dancers).length
                    )
                );
            })
        )
    );
};

var OrganizerFinances = function (_React$Component) {
    _inherits(OrganizerFinances, _React$Component);

    function OrganizerFinances(props) {
        _classCallCheck(this, OrganizerFinances);

        var _this = _possibleConstructorReturn(this, (OrganizerFinances.__proto__ || Object.getPrototypeOf(OrganizerFinances)).call(this, props));

        _this.state = { teams: _this.props.teams };
        return _this;
    }

    _createClass(OrganizerFinances, [{
        key: "updateReceivedAmount",
        value: function updateReceivedAmount() {
            var _this2 = this;

            var receivedAmounts = document.querySelectorAll('.team-received');
            var teamsDict = {};
            receivedAmounts.forEach(function (t) {
                return teamsDict[t.dataset.teamId] = t.value !== "" ? t.value * 100 : Number(t.dataset.placeholder);
            });
            fetch("/api/teams/update_received_amount", { method: "PATCH", credentials: 'same-origin', body: JSON.stringify(teamsDict) }).then(function (response) {
                return response.json();
            }).then(function (result) {
                var newState = _this2.state.teams;
                Object.values(newState).forEach(function (t) {
                    return t.finances_data.prices.team = Number(result[t.team_id]);
                });
                _this2.setState({ teams: newState });
                receivedAmounts.forEach(function (i) {
                    return i.value = "";
                });
                $(function () {
                    $('[data-toggle="tooltip"]').tooltip("dispose").tooltip();
                });
            }).catch(function (error) {
                console.log('Error: \n', error);
            });
        }
    }, {
        key: "giveRefund",
        value: function giveRefund(dancer, flag) {
            var _this3 = this;

            fetch("/api/contestants/" + dancer.contestant_id + "/give_refund/" + Number(flag), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                var newState = _this3.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                _this3.setState({ teams: newState });
            }).catch(function (error) {
                console.log('Error: \n', error);
            });
        }
    }, {
        key: "removePaymentRequirement",
        value: function removePaymentRequirement(dancer, flag) {
            var _this4 = this;

            fetch("/api/contestants/" + dancer.contestant_id + "/remove_payment_requirement/", { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                var newState = _this4.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                _this4.setState({ teams: newState });
            }).catch(function (error) {
                console.log('Error: \n', error);
            });
        }
    }, {
        key: "render",
        value: function render() {
            var _this5 = this;

            var teams = Object.values(this.state.teams);
            var activeTeams = teams.filter(filterTeamsWithDancers);
            var DutchTeams = activeTeams.filter(filterDutchTeams);
            var GermanTeams = activeTeams.filter(filterGermanTeams);
            var OtherTeams = activeTeams.filter(filterOtherTeams);

            var dancers = [].concat.apply([], teams.map(function (team) {
                return Object.values(team.finances_data.dancers);
            }));
            var students = dancers.filter(filterStudents);
            var phdStudents = dancers.filter(filterPhDStudents);
            var nonStudents = dancers.filter(filterNonStudents);
            var dancersWithMerchandise = dancers.filter(filterHasMerchandise);
            var merchandise = dancersWithMerchandise.map(function (dancer) {
                return Object.values(dancer.merchandise_info.purchases).length;
            }).reduce(reduceArraySum, 0);

            var dancersOwedPrice = dancers.map(mapPaymentPrice).reduce(reduceArraySum, 0);
            var teamsReceivedPrice = activeTeams.map(function (team) {
                return team.finances_data.prices.team;
            }).reduce(reduceArraySum, 0);
            var differencePrice = teamsReceivedPrice - dancersOwedPrice;
            var dancersWithRefund = dancers.filter(filterHasRefund);
            var refundPrice = dancersWithRefund.map(mapRefundPrice).reduce(reduceArraySum, 0);

            var cancelledDancers = dancers.filter(filterCancelled);
            var noRefundDancers = cancelledDancers.filter(filterDoesNotHaveRefund).filter(filterPaymentRequired);
            var refundDancers = cancelledDancers.filter(filterHasRefund);

            return React.createElement(
                React.Fragment,
                null,
                React.createElement(
                    "h2",
                    null,
                    "Financial overview"
                ),
                React.createElement(
                    "p",
                    null,
                    "Don't forget to save any changes made here."
                ),
                React.createElement(
                    "ul",
                    { className: "nav nav-tabs", id: "myTabs", role: "tablist" },
                    React.createElement(
                        "li",
                        { className: "nav-item", role: "presentation" },
                        React.createElement(
                            "a",
                            { className: "nav-link active", href: "#all-teams", id: "all-teams-tab", role: "tab", "data-toggle": "tab" },
                            "All teams"
                        )
                    ),
                    DutchTeams.length > 0 ? React.createElement(OrganizerFinancesDropDown, { text: "Dutch", teams: DutchTeams }) : null,
                    GermanTeams.length > 0 ? React.createElement(OrganizerFinancesDropDown, { text: "German", teams: GermanTeams }) : null,
                    OtherTeams.length > 0 ? React.createElement(OrganizerFinancesDropDown, { text: "Other", teams: OtherTeams }) : null,
                    dancersWithRefund.length > 0 ? React.createElement(
                        "li",
                        { className: "nav-item", role: "presentation" },
                        React.createElement(
                            "a",
                            { className: "nav-link", href: "#refunds", id: "refunds-tab", role: "tab", "data-toggle": "tab" },
                            "Refunds"
                        )
                    ) : null
                ),
                React.createElement(
                    "div",
                    { className: "tab-content" },
                    React.createElement(
                        "div",
                        { className: "tab-pane fade show active", id: "all-teams" },
                        React.createElement(
                            "form",
                            { method: "POST", encType: "multipart/form-data", noValidate: true },
                            React.createElement("input", { className: "btn btn-outline-primary float-right my-2", id: "submit-download_file", name: "download_file", type: "submit", value: "Download overview" })
                        ),
                        React.createElement(
                            "button",
                            { className: "btn btn-outline-primary my-2", type: "button", onClick: function onClick() {
                                    return _this5.updateReceivedAmount();
                                } },
                            "Save changes"
                        ),
                        React.createElement(
                            "table",
                            { className: "table table-sm" },
                            React.createElement(
                                "thead",
                                null,
                                React.createElement(
                                    "tr",
                                    { className: "finances-summary-row" },
                                    this.props.settings.phd_student_category ? React.createElement(
                                        React.Fragment,
                                        null,
                                        React.createElement(
                                            "th",
                                            { style: { width: '18%' } },
                                            "Team"
                                        ),
                                        React.createElement(
                                            "th",
                                            { style: { width: '10%' } },
                                            "Students"
                                        ),
                                        React.createElement(
                                            "th",
                                            { style: { width: '10%' } },
                                            "PhD students"
                                        )
                                    ) : React.createElement(
                                        React.Fragment,
                                        null,
                                        React.createElement(
                                            "th",
                                            { style: { width: '28%' } },
                                            "Team"
                                        ),
                                        React.createElement(
                                            "th",
                                            { style: { width: '10%' } },
                                            "Students"
                                        )
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '10%' } },
                                        "Non students"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '10%' } },
                                        this.props.settings.merchandise ? "Merchandise" : null
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '13%' } },
                                        "Owed"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '9%' } },
                                        "Received"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '8%' } },
                                        "Difference"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '12%' } },
                                        "Refund"
                                    )
                                )
                            ),
                            React.createElement(
                                "tbody",
                                null,
                                activeTeams.sort(sortTeamsAlphabetically).map(function (t) {
                                    var dancers = Object.values(t.finances_data.dancers);
                                    var students = dancers.filter(filterStudents);
                                    var phdStudents = dancers.filter(filterPhDStudents);
                                    var nonStudents = dancers.filter(filterNonStudents);
                                    var dancersWithMerchandise = dancers.filter(filterHasMerchandise);
                                    var merchandise = dancersWithMerchandise.map(function (dancer) {
                                        return Object.values(dancer.merchandise_info.purchases).length;
                                    }).reduce(reduceArraySum, 0);

                                    var dancersOwedPrice = dancers.map(mapPaymentPrice).reduce(reduceArraySum, 0);
                                    var differencePrice = t.finances_data.prices.team - dancersOwedPrice;
                                    var refundPrice = dancers.filter(filterHasRefund).map(mapRefundPrice).reduce(reduceArraySum, 0);

                                    return React.createElement(
                                        "tr",
                                        { className: "finances-summary-row " + (differencePrice === 0 ? "table-success" : differencePrice > 0 ? "table-warning" : "table-danger"), key: "team-total-" + t.team_id },
                                        React.createElement(
                                            "td",
                                            null,
                                            t.name
                                        ),
                                        React.createElement(
                                            "td",
                                            null,
                                            students.length
                                        ),
                                        _this5.props.settings.phd_student_category ? React.createElement(
                                            "td",
                                            null,
                                            phdStudents.length
                                        ) : null,
                                        React.createElement(
                                            "td",
                                            null,
                                            nonStudents.length
                                        ),
                                        React.createElement(
                                            "td",
                                            null,
                                            _this5.props.settings.merchandise ? merchandise : null
                                        ),
                                        React.createElement(
                                            "td",
                                            null,
                                            currencyFormat(dancersOwedPrice)
                                        ),
                                        React.createElement(
                                            "td",
                                            null,
                                            React.createElement("input", { className: "form-control text-right px-0 py-0 team-received",
                                                style: { height: "auto" }, type: "number", min: "0", step: "0.01",
                                                placeholder: currencyFormat(t.finances_data.prices.team),
                                                "data-toggle": "tooltip", "data-placement": "top",
                                                "data-team-id": t.team_id, "data-placeholder": t.finances_data.prices.team,
                                                title: currencyFormat(t.finances_data.prices.team) })
                                        ),
                                        React.createElement(
                                            "td",
                                            null,
                                            currencyFormat(differencePrice)
                                        ),
                                        React.createElement(
                                            "td",
                                            null,
                                            currencyFormat(refundPrice)
                                        )
                                    );
                                }),
                                React.createElement(
                                    "tr",
                                    { className: "finances-summary-row" },
                                    React.createElement("th", null),
                                    React.createElement(
                                        "th",
                                        null,
                                        students.length
                                    ),
                                    this.props.settings.phd_student_category ? React.createElement(
                                        "th",
                                        null,
                                        phdStudents.length
                                    ) : null,
                                    React.createElement(
                                        "th",
                                        null,
                                        nonStudents.length
                                    ),
                                    React.createElement(
                                        "th",
                                        null,
                                        this.props.settings.merchandise ? merchandise : null
                                    ),
                                    React.createElement(
                                        "th",
                                        null,
                                        currencyFormat(dancersOwedPrice)
                                    ),
                                    React.createElement(
                                        "th",
                                        null,
                                        currencyFormat(teamsReceivedPrice)
                                    ),
                                    React.createElement(
                                        "th",
                                        null,
                                        currencyFormat(differencePrice)
                                    ),
                                    React.createElement(
                                        "th",
                                        null,
                                        currencyFormat(refundPrice)
                                    )
                                )
                            )
                        )
                    ),
                    activeTeams.sort(sortTeamsAlphabetically).map(function (t) {
                        return React.createElement(
                            "div",
                            { className: "tab-pane fade", id: "tab-" + t.team_id, key: "tab-" + t.team_id, role: "tabpanel" },
                            React.createElement(TeamCaptainFinances, { dancers: t.finances_data.dancers, settings: t.finances_data.settings, prices: t.finances_data.prices, merchandise_items: t.finances_data.merchandise_items })
                        );
                    }),
                    cancelledDancers.length > 0 ? React.createElement(
                        "div",
                        { className: "tab-pane fade", id: "refunds" },
                        React.createElement(
                            "table",
                            { className: "table table-sm table-finances mt-2" },
                            React.createElement(
                                "thead",
                                null,
                                React.createElement(
                                    "tr",
                                    null,
                                    React.createElement(
                                        "th",
                                        { className: "font-size-4", colSpan: "4" },
                                        "Cancelled dancers"
                                    )
                                ),
                                React.createElement(
                                    "tr",
                                    null,
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' } },
                                        "Dancer"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' } },
                                        "Team"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' }, className: "text-right" },
                                        "Potential refund"
                                    ),
                                    React.createElement("th", { style: { width: '40%' } })
                                )
                            ),
                            React.createElement(
                                "tbody",
                                null,
                                noRefundDancers.sort(sortDancersAlphabetically).map(function (d) {
                                    return React.createElement(
                                        "tr",
                                        { key: 'row' + ("" + d.contestant_id) },
                                        React.createElement(
                                            "td",
                                            null,
                                            d.full_name
                                        ),
                                        React.createElement(
                                            "td",
                                            null,
                                            d.contestant_info.team
                                        ),
                                        React.createElement(
                                            "td",
                                            { className: "text-right" },
                                            currencyFormat(d.payment_info.potential_refund_price)
                                        ),
                                        React.createElement(
                                            "td",
                                            { className: "text-right" },
                                            React.createElement(
                                                "button",
                                                { className: "btn btn-warning btn-sm my-1 mx-2", onClick: function onClick() {
                                                        return _this5.giveRefund(d, true);
                                                    } },
                                                "Give refund"
                                            ),
                                            React.createElement(
                                                "button",
                                                { className: "btn btn-danger btn-sm my-1 mx-2", "data-toggle": "modal", "data-target": '#remove-modal-' + ("" + d.contestant_id),
                                                    "data-keyboard": "false", "data-backdrop": "static" },
                                                "Remove payment requirement"
                                            )
                                        )
                                    );
                                }),
                                React.createElement(
                                    "tr",
                                    null,
                                    React.createElement(
                                        "th",
                                        { className: "font-size-4", colSpan: "4" },
                                        "Refunds"
                                    )
                                ),
                                React.createElement(
                                    "tr",
                                    null,
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' } },
                                        "Dancer"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' } },
                                        "Refund reason(s)"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' }, className: "text-right" },
                                        "Refund"
                                    ),
                                    React.createElement("th", { style: { width: '40%' } })
                                ),
                                refundDancers.sort(sortDancersAlphabetically).map(function (d) {
                                    return React.createElement(
                                        "tr",
                                        { key: 'row' + ("" + d.contestant_id) },
                                        React.createElement(
                                            "td",
                                            null,
                                            d.full_name
                                        ),
                                        React.createElement(
                                            "td",
                                            null,
                                            d.payment_info.refund_reasons.map(function (r) {
                                                return React.createElement(
                                                    "div",
                                                    { key: 'reason-' + r + ("" + d.contestant_id) },
                                                    r
                                                );
                                            })
                                        ),
                                        React.createElement(
                                            "td",
                                            { className: "text-right" },
                                            currencyFormat(d.payment_info.refund_price)
                                        ),
                                        React.createElement(
                                            "td",
                                            { className: "text-right" },
                                            React.createElement(
                                                "button",
                                                { className: "btn btn-warning btn-sm my-1 mx-2", onClick: function onClick() {
                                                        return _this5.giveRefund(d, false);
                                                    } },
                                                "Remove refund"
                                            )
                                        )
                                    );
                                })
                            )
                        )
                    ) : null
                ),
                noRefundDancers.sort(sortDancersAlphabetically).map(function (d) {
                    return React.createElement(
                        "div",
                        { className: "modal fade", id: 'remove-modal-' + ("" + d.contestant_id), key: 'remove-modal-' + ("" + d.contestant_id), tabIndex: "-1", role: "dialog", "data-keyboard": "false", "data-backdrop": "static" },
                        React.createElement(
                            "div",
                            { className: "modal-dialog modal-lg", role: "document" },
                            React.createElement(
                                "div",
                                { className: "modal-content" },
                                React.createElement(
                                    "div",
                                    { className: "modal-header" },
                                    React.createElement(
                                        "h5",
                                        { className: "modal-title" },
                                        "Remove payment requirement"
                                    ),
                                    React.createElement(
                                        "button",
                                        { type: "button", className: "close", "data-dismiss": "modal", "aria-label": "Close" },
                                        React.createElement(
                                            "span",
                                            { "aria-hidden": "true" },
                                            "\xD7"
                                        )
                                    )
                                ),
                                React.createElement(
                                    "div",
                                    { className: "modal-body" },
                                    React.createElement(
                                        "p",
                                        null,
                                        "You are about to remove the payment requirement of ",
                                        d.full_name,
                                        "."
                                    ),
                                    React.createElement(
                                        "p",
                                        null,
                                        "Are you sure you wish to do this?"
                                    )
                                ),
                                React.createElement(
                                    "div",
                                    { className: "modal-footer" },
                                    React.createElement(
                                        "button",
                                        { type: "button", className: "btn btn-secondary", "data-dismiss": "modal" },
                                        "No"
                                    ),
                                    React.createElement(
                                        "button",
                                        { type: "button", className: "btn btn-primary", "data-dismiss": "modal", onClick: function onClick() {
                                                return _this5.removePaymentRequirement(d);
                                            } },
                                        "Yes"
                                    )
                                )
                            )
                        )
                    );
                })
            );
        }
    }]);

    return OrganizerFinances;
}(React.Component);