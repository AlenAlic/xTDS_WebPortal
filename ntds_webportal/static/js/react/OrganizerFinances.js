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
        key: "giveEntryFeeRefund",
        value: function giveEntryFeeRefund(dancer) {
            var _this3 = this;

            fetch("/api/contestants/" + dancer.contestant_id + "/give_entry_fee_refund", { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
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
        key: "giveGeneralRefund",
        value: function giveGeneralRefund() {
            var _this5 = this;

            var dancer = document.getElementById("general-dancer");
            var contestant_id = dancer.options[dancer.selectedIndex].value;
            var name = dancer.options[dancer.selectedIndex].innerText;
            var data = {
                "reason": document.getElementById("general-reason").value,
                "amount": document.getElementById("general-amount").value
            };
            dancer.selectedIndex = 0;
            document.getElementById("general-reason").value = "";
            document.getElementById("general-amount").value = "";
            fetch("/api/contestants/" + contestant_id + "/give_general_refund", { method: "PATCH", credentials: 'same-origin', body: JSON.stringify(data) }).then(function (response) {
                return response.json();
            }).then(function (result) {
                var newState = _this5.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                _this5.setState({ teams: newState });
                $.notify({ message: "Refund given to " + name + "." }, { type: 'alert-info' });
            }).catch(function (error) {
                console.log('Error: \n', error);
            });
        }
    }, {
        key: "updateRefund",
        value: function updateRefund(dancer, refund) {
            var _this6 = this;

            var data = {
                "reason": document.getElementById("reason-" + refund.refund_id).value,
                "amount": document.getElementById("amount-" + refund.refund_id).value
            };
            fetch("/api/contestants/" + dancer.contestant_id + "/update_refund/" + refund.refund_id, { method: "PATCH", credentials: 'same-origin', body: JSON.stringify(data) }).then(function (response) {
                return response.json();
            }).then(function (result) {
                var newState = _this6.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                _this6.setState({ teams: newState });
            }).catch(function (error) {
                console.log('Error: \n', error);
            });
        }
    }, {
        key: "deleteRefund",
        value: function deleteRefund(dancer, refund) {
            var _this7 = this;

            fetch("/api/contestants/" + dancer.contestant_id + "/delete_refund/" + refund.refund_id, { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                var newState = _this7.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                _this7.setState({ teams: newState });
            }).catch(function (error) {
                console.log('Error: \n', error);
            });
        }
    }, {
        key: "render",
        value: function render() {
            var _this8 = this;

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
            var refundDancers = dancers.filter(filterHasRefund);

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
                    React.createElement(
                        "li",
                        { className: "nav-item", role: "presentation" },
                        React.createElement(
                            "a",
                            { className: dancersWithRefund.length > 0 ? "nav-link" : "nav-link disabled", href: "#refunds", id: "refunds-tab", role: "tab", "data-toggle": "tab" },
                            "Refunds"
                        )
                    )
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
                                    return _this8.updateReceivedAmount();
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
                                        _this8.props.settings.phd_student_category ? React.createElement(
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
                                            _this8.props.settings.merchandise ? merchandise : null
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
                        noRefundDancers.length > 0 ? React.createElement(
                            "table",
                            { className: "table table-sm mt-2" },
                            React.createElement(
                                "tbody",
                                null,
                                React.createElement(
                                    "tr",
                                    null,
                                    React.createElement(
                                        "th",
                                        { className: "font-size-4", colSpan: "5" },
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
                                        { style: { width: '40%' } },
                                        "Team"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' }, className: "text-right" },
                                        "Potential refund"
                                    ),
                                    React.createElement("th", { style: { width: '20%' } })
                                ),
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
                                            currencyFormat(d.payment_info.entry_price_refund)
                                        ),
                                        React.createElement(
                                            "td",
                                            { className: "text-right" },
                                            React.createElement(
                                                "button",
                                                { className: "btn btn-danger btn-sm d-inline-block my-1", "data-toggle": "modal", "data-target": '#remove-modal-' + ("" + d.contestant_id),
                                                    "data-keyboard": "false", "data-backdrop": "static" },
                                                "Remove payment requirement"
                                            ),
                                            React.createElement(
                                                "button",
                                                { className: "btn btn-warning btn-sm d-inline-block my-1", onClick: function onClick() {
                                                        return _this8.giveEntryFeeRefund(d);
                                                    } },
                                                "Give entry fee refund"
                                            )
                                        )
                                    );
                                })
                            )
                        ) : null,
                        React.createElement(
                            "div",
                            { className: "card mt-2" },
                            React.createElement(
                                "div",
                                { className: "card-body" },
                                React.createElement(
                                    "h5",
                                    { className: "card-title" },
                                    "Give refund"
                                ),
                                React.createElement(
                                    "form",
                                    { className: "form", method: "POST", encType: "multipart/form-data", noValidate: true },
                                    React.createElement(
                                        "div",
                                        { className: "form-group" },
                                        React.createElement(
                                            "label",
                                            { htmlFor: "general-dancer" },
                                            "Dancer"
                                        ),
                                        React.createElement(
                                            "select",
                                            { className: "form-control", id: "general-dancer" },
                                            React.createElement(
                                                "option",
                                                { value: 0 },
                                                "Select dancer"
                                            ),
                                            dancers.sort(sortDancersAlphabetically).map(function (d) {
                                                return React.createElement(
                                                    "option",
                                                    { key: 'option-' + ("" + d.contestant_id), value: d.contestant_id },
                                                    d.full_name
                                                );
                                            })
                                        )
                                    ),
                                    React.createElement(
                                        "div",
                                        { className: "form-group" },
                                        React.createElement(
                                            "label",
                                            { htmlFor: "general-reason" },
                                            "Refund reason"
                                        ),
                                        React.createElement("input", { type: "text", className: "form-control", id: "general-reason" })
                                    ),
                                    React.createElement(
                                        "div",
                                        { className: "form-group" },
                                        React.createElement(
                                            "label",
                                            { htmlFor: "general-amount" },
                                            "Refund amount (eurocents)"
                                        ),
                                        React.createElement("input", { type: "number", className: "form-control", id: "general-amount", min: "0", step: "1" })
                                    ),
                                    React.createElement(
                                        "button",
                                        { type: "button", className: "btn btn-primary", onClick: function onClick() {
                                                return _this8.giveGeneralRefund();
                                            } },
                                        "Give refund"
                                    )
                                )
                            )
                        ),
                        React.createElement(
                            "table",
                            { className: "table table-sm mt-2" },
                            React.createElement(
                                "tbody",
                                null,
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
                                        { style: { width: '40%' } },
                                        "Refund"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' }, className: "text-right" },
                                        "Amount"
                                    ),
                                    React.createElement("th", { style: { width: '20%' }, className: "text-right" })
                                ),
                                refundDancers.sort(sortDancersAlphabetically).map(function (d) {
                                    return React.createElement(
                                        React.Fragment,
                                        { key: 'row-' + ("-" + d.contestant_id) },
                                        d.payment_info.refunds.map(function (r, i) {
                                            return i === 0 ? React.createElement(
                                                "tr",
                                                { key: 'row-' + r.refund_id + ("-" + d.contestant_id) },
                                                React.createElement(
                                                    "td",
                                                    null,
                                                    d.full_name
                                                ),
                                                React.createElement(
                                                    "td",
                                                    null,
                                                    r.reason
                                                ),
                                                React.createElement(
                                                    "td",
                                                    { className: "text-right " },
                                                    currencyFormat(r.amount)
                                                ),
                                                React.createElement(
                                                    "td",
                                                    { className: "text-right" },
                                                    React.createElement(
                                                        "button",
                                                        { className: "btn btn-info btn-sm", "data-toggle": "modal", "data-target": '#update-modal-' + r.refund_id,
                                                            "data-keyboard": "false", "data-backdrop": "static" },
                                                        "Edit"
                                                    ),
                                                    React.createElement(
                                                        "button",
                                                        { className: "btn btn-danger btn-sm ml-1", "data-toggle": "modal", "data-target": '#delete-modal-' + r.refund_id,
                                                            "data-keyboard": "false", "data-backdrop": "static" },
                                                        "Delete"
                                                    )
                                                )
                                            ) : React.createElement(
                                                "tr",
                                                { key: 'row-' + r.refund_id + ("-" + d.contestant_id) },
                                                React.createElement("td", { className: "border-0" }),
                                                React.createElement(
                                                    "td",
                                                    { className: "border-0" },
                                                    r.reason
                                                ),
                                                React.createElement(
                                                    "td",
                                                    { className: "border-0 text-right" },
                                                    currencyFormat(r.amount)
                                                ),
                                                React.createElement(
                                                    "td",
                                                    { className: "border-0 text-right" },
                                                    React.createElement(
                                                        "button",
                                                        { className: "btn btn-info btn-sm", "data-toggle": "modal", "data-target": '#update-modal-' + r.refund_id,
                                                            "data-keyboard": "false", "data-backdrop": "static" },
                                                        "Edit"
                                                    ),
                                                    React.createElement(
                                                        "button",
                                                        { className: "btn btn-danger btn-sm ml-1", "data-toggle": "modal", "data-target": '#delete-modal-' + r.refund_id,
                                                            "data-keyboard": "false", "data-backdrop": "static" },
                                                        "Delete"
                                                    )
                                                )
                                            );
                                        }),
                                        React.createElement(
                                            "tr",
                                            null,
                                            React.createElement("td", { className: "border-0" }),
                                            React.createElement(
                                                "td",
                                                { className: "border-0 text-right" },
                                                React.createElement(
                                                    "b",
                                                    null,
                                                    "Total"
                                                )
                                            ),
                                            React.createElement(
                                                "td",
                                                { className: "border-0 text-right" },
                                                React.createElement(
                                                    "b",
                                                    null,
                                                    currencyFormat(d.payment_info.refund_price)
                                                )
                                            ),
                                            React.createElement("td", { className: "border-0 text-right" })
                                        )
                                    );
                                })
                            )
                        )
                    ) : null
                ),
                noRefundDancers.map(function (d) {
                    return React.createElement(
                        "div",
                        { className: "modal fade", id: 'remove-modal-' + ("" + d.contestant_id), key: 'remove-add-modal-' + ("" + d.contestant_id), tabIndex: "-1", role: "dialog", "data-keyboard": "false", "data-backdrop": "static" },
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
                                                return _this8.removePaymentRequirement(d);
                                            } },
                                        "Yes"
                                    )
                                )
                            )
                        )
                    );
                }),
                refundDancers.map(function (d) {
                    return d.payment_info.refunds.map(function (r) {
                        return React.createElement(
                            React.Fragment,
                            { key: 'modals-' + r.refund_id },
                            React.createElement(
                                "div",
                                { className: "modal fade", id: 'update-modal-' + r.refund_id, tabIndex: "-1", role: "dialog", "data-keyboard": "false", "data-backdrop": "static" },
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
                                                "Edit refund"
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
                                                "div",
                                                { className: "form-group" },
                                                React.createElement(
                                                    "label",
                                                    { htmlFor: 'reason-' + r.refund_id },
                                                    "Refund reason"
                                                ),
                                                React.createElement("input", { type: "text", className: "form-control", id: 'reason-' + r.refund_id, defaultValue: r.reason })
                                            ),
                                            React.createElement(
                                                "div",
                                                { className: "form-group" },
                                                React.createElement(
                                                    "label",
                                                    { htmlFor: 'amount-' + r.refund_id },
                                                    "Refund amount (eurocents)"
                                                ),
                                                React.createElement("input", { type: "text", className: "form-control", id: 'amount-' + r.refund_id, defaultValue: r.amount })
                                            )
                                        ),
                                        React.createElement(
                                            "div",
                                            { className: "modal-footer" },
                                            React.createElement(
                                                "button",
                                                { type: "button", className: "btn btn-secondary", "data-dismiss": "modal" },
                                                "Cancel"
                                            ),
                                            React.createElement(
                                                "button",
                                                { type: "button", className: "btn btn-primary", "data-dismiss": "modal", onClick: function onClick() {
                                                        return _this8.updateRefund(d, r);
                                                    } },
                                                "Save"
                                            )
                                        )
                                    )
                                )
                            ),
                            React.createElement(
                                "div",
                                { className: "modal fade", id: 'delete-modal-' + r.refund_id, tabIndex: "-1", role: "dialog", "data-keyboard": "false", "data-backdrop": "static" },
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
                                                "Delete refund"
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
                                                "You are about to remove the refund of ",
                                                d.full_name,
                                                " for ",
                                                r.reason,
                                                " (",
                                                currencyFormat(r.amount),
                                                ")."
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
                                                        return _this8.deleteRefund(d, r);
                                                    } },
                                                "Yes"
                                            )
                                        )
                                    )
                                )
                            )
                        );
                    });
                })
            );
        }
    }]);

    return OrganizerFinances;
}(React.Component);