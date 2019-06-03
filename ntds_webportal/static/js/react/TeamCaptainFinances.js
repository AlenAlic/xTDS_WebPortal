var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var TeamCaptainFinances = function (_React$Component) {
    _inherits(TeamCaptainFinances, _React$Component);

    function TeamCaptainFinances(props) {
        _classCallCheck(this, TeamCaptainFinances);

        var _this = _possibleConstructorReturn(this, (TeamCaptainFinances.__proto__ || Object.getPrototypeOf(TeamCaptainFinances)).call(this, props));

        _this.state = { dancers: _this.props.dancers };
        return _this;
    }

    _createClass(TeamCaptainFinances, [{
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
            var _this2 = this;

            this.setPending(dancer);
            var newState = this.state.dancers;
            fetch("/api/contestants/" + dancer.contestant_id + "/entry_payment/" + Number(!dancer.payment_info.entry_paid), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                newState[result.contestant_id] = result;
                _this2.setState({ dancers: newState });
            }).catch(function (error) {
                console.log('Error: \n', error);
                dancer.pending = false;
                newState[dancer.contestant_id] = dancer;
                _this2.setState({ dancers: newState });
            });
        }
    }, {
        key: "allPayment",
        value: function allPayment(dancer) {
            var _this3 = this;

            this.setPending(dancer);
            var newState = this.state.dancers;
            fetch("/api/contestants/" + dancer.contestant_id + "/all_payment/" + Number(!dancer.payment_info.all_paid), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
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
        key: "render",
        value: function render() {
            var _this5 = this;

            var phdCategory = this.props.settings.phd_student_category;
            var merchandiseSold = this.props.settings.merchandise;

            var dancers = Object.values(this.state.dancers);

            var students = dancers.filter(filterStudents);
            var phdStudents = dancers.filter(filterPhDStudents);
            var nonStudents = dancers.filter(filterNonStudents);

            var studentsPaid = students.filter(filterEntryPaid);
            var phdStudentsPaid = phdStudents.filter(filterEntryPaid);
            var nonStudentsPaid = nonStudents.filter(filterEntryPaid);

            var studentsRemaining = students.length - studentsPaid.length;
            var phdStudentsRemaining = phdStudents.length - phdStudentsPaid.length;
            var nonStudentsRemaining = nonStudents.length - nonStudentsPaid.length;

            var studentsOwedPrice = students.map(mapEntryPrice).reduce(reduceArraySum, 0);
            var phdStudentsOwedPrice = phdStudents.map(mapEntryPrice).reduce(reduceArraySum, 0);
            var nonStudentsOwedPrice = nonStudents.map(mapEntryPrice).reduce(reduceArraySum, 0);

            var studentsPaidPrice = studentsPaid.map(mapEntryPrice).reduce(reduceArraySum, 0);
            var phdStudentsPaidPrice = phdStudentsPaid.map(mapEntryPrice).reduce(reduceArraySum, 0);
            var nonStudentsPaidPrice = nonStudentsPaid.map(mapEntryPrice).reduce(reduceArraySum, 0);

            var studentsRemainingPrice = studentsOwedPrice - studentsPaidPrice;
            var phdStudentsRemainingPrice = phdStudentsOwedPrice - phdStudentsPaidPrice;
            var nonStudentsRemainingPrice = nonStudentsOwedPrice - nonStudentsPaidPrice;

            var dancerOwed = dancers.length;
            var dancersPaid = studentsPaid.length + phdStudentsPaid.length + nonStudentsPaid.length;
            var dancersRemaining = dancerOwed - dancersPaid;

            var dancersOwedPrice = studentsOwedPrice + phdStudentsOwedPrice + nonStudentsOwedPrice;
            var dancersPaidPrice = studentsPaidPrice + phdStudentsPaidPrice + nonStudentsPaidPrice;
            var dancersRemainingPrice = dancersOwedPrice - dancersPaidPrice;

            var dancersWithMerchandise = dancers.filter(filterHasMerchandise);

            var merchandiseContainer = {};
            var merchandisePaidContainer = {};
            Object.values(this.props.merchandise_items).forEach(function (m) {
                merchandiseContainer[m.merchandise_item_id] = 0;
                merchandisePaidContainer[m.merchandise_item_id] = 0;
            });
            dancersWithMerchandise.forEach(function (d) {
                return Object.values(d.merchandise_info.purchases).forEach(function (p) {
                    return merchandiseContainer[p.merchandise_item_id] += 1;
                });
            });
            dancersWithMerchandise.forEach(function (d) {
                return Object.values(d.merchandise_info.purchases).filter(filterHasMerchandisePaid).forEach(function (p) {
                    return merchandisePaidContainer[p.merchandise_item_id] += 1;
                });
            });
            var merchandisePriceContainer = {};
            var merchandisePaidPriceContainer = {};
            Object.values(this.props.merchandise_items).forEach(function (m) {
                merchandisePriceContainer[m.merchandise_item_id] = merchandiseContainer[m.merchandise_item_id] * _this5.props.merchandise_items[m.merchandise_item_id].price;
                merchandisePaidPriceContainer[m.merchandise_item_id] = merchandisePaidContainer[m.merchandise_item_id] * _this5.props.merchandise_items[m.merchandise_item_id].price;
            });

            var merchandiseOwed = arrSum(Object.values(merchandiseContainer));
            var merchandisePaid = arrSum(Object.values(merchandisePaidContainer));
            var merchandiseRemaining = merchandiseOwed - merchandisePaid;

            var merchandiseOwedPrice = arrSum(Object.values(merchandisePriceContainer));
            var merchandisePaidPrice = arrSum(Object.values(merchandisePaidPriceContainer));
            var merchandiseRemainingPrice = merchandiseOwedPrice - merchandisePaidPrice;

            return React.createElement(
                React.Fragment,
                null,
                React.createElement(
                    "h2",
                    null,
                    "Summary"
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
                            React.createElement(
                                "th",
                                { style: { width: '26%' } },
                                "Dancers"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' } },
                                "#"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '8%' } },
                                "Owed"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '20%' } },
                                "#"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' } },
                                "Paid"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '18%' } },
                                "#"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '8%' } },
                                "Remaining"
                            )
                        )
                    ),
                    React.createElement(
                        "tbody",
                        null,
                        React.createElement(
                            "tr",
                            { className: "finances-summary-row" },
                            React.createElement(
                                "td",
                                null,
                                "Students:"
                            ),
                            React.createElement(
                                "td",
                                null,
                                students.length
                            ),
                            React.createElement(
                                "td",
                                null,
                                currencyFormat(studentsOwedPrice)
                            ),
                            React.createElement(
                                "td",
                                null,
                                studentsPaid.length
                            ),
                            React.createElement(
                                "td",
                                null,
                                currencyFormat(studentsPaidPrice)
                            ),
                            React.createElement(
                                "td",
                                null,
                                studentsRemaining
                            ),
                            React.createElement(
                                "td",
                                null,
                                currencyFormat(studentsRemainingPrice)
                            )
                        ),
                        phdCategory ? React.createElement(
                            "tr",
                            { className: "finances-summary-row" },
                            React.createElement(
                                "td",
                                null,
                                "PhD-students:"
                            ),
                            React.createElement(
                                "td",
                                null,
                                phdStudents.length
                            ),
                            React.createElement(
                                "td",
                                null,
                                currencyFormat(phdStudentsOwedPrice)
                            ),
                            React.createElement(
                                "td",
                                null,
                                phdStudentsPaid.length
                            ),
                            React.createElement(
                                "td",
                                null,
                                currencyFormat(phdStudentsPaidPrice)
                            ),
                            React.createElement(
                                "td",
                                null,
                                phdStudentsRemaining
                            ),
                            React.createElement(
                                "td",
                                null,
                                currencyFormat(phdStudentsRemainingPrice)
                            )
                        ) : null,
                        React.createElement(
                            "tr",
                            { className: "finances-summary-row" },
                            React.createElement(
                                "td",
                                null,
                                "Non-students:"
                            ),
                            React.createElement(
                                "td",
                                null,
                                nonStudents.length
                            ),
                            React.createElement(
                                "td",
                                null,
                                currencyFormat(nonStudentsOwedPrice)
                            ),
                            React.createElement(
                                "td",
                                null,
                                nonStudentsPaid.length
                            ),
                            React.createElement(
                                "td",
                                null,
                                currencyFormat(nonStudentsPaidPrice)
                            ),
                            React.createElement(
                                "td",
                                null,
                                nonStudentsRemaining
                            ),
                            React.createElement(
                                "td",
                                null,
                                currencyFormat(nonStudentsRemainingPrice)
                            )
                        ),
                        merchandiseSold ? React.createElement(
                            React.Fragment,
                            null,
                            React.createElement(
                                "tr",
                                { className: "finances-summary-row" },
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    React.createElement(
                                        "i",
                                        null,
                                        "Subtotal"
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        dancerOwed
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        currencyFormat(dancersOwedPrice)
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        dancersPaid
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        currencyFormat(dancersPaidPrice)
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        dancersRemaining
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        currencyFormat(dancersRemainingPrice)
                                    )
                                )
                            ),
                            React.createElement(
                                "tr",
                                null,
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "b",
                                        null,
                                        "Merchandise"
                                    )
                                ),
                                React.createElement("td", { colSpan: "6" })
                            ),
                            Object.values(this.props.merchandise_items).sort(sortMerchandiseAlphabetically).map(function (m) {
                                return React.createElement(
                                    "tr",
                                    { className: "finances-summary-row", key: 'row' + ("" + m.merchandise_item_id) },
                                    React.createElement(
                                        "td",
                                        null,
                                        m.description
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        merchandiseContainer[m.merchandise_item_id]
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        currencyFormat(merchandiseContainer[m.merchandise_item_id] * m.price)
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        merchandisePaidContainer[m.merchandise_item_id]
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        currencyFormat(merchandisePaidContainer[m.merchandise_item_id] * m.price)
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        merchandiseContainer[m.merchandise_item_id] - merchandisePaidContainer[m.merchandise_item_id]
                                    ),
                                    React.createElement(
                                        "td",
                                        null,
                                        currencyFormat((merchandiseContainer[m.merchandise_item_id] - merchandisePaidContainer[m.merchandise_item_id]) * m.price)
                                    )
                                );
                            }),
                            React.createElement(
                                "tr",
                                { className: "finances-summary-row" },
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    React.createElement(
                                        "i",
                                        null,
                                        "Subtotal"
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        merchandiseOwed
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        currencyFormat(merchandiseOwedPrice)
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        merchandisePaid
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        currencyFormat(merchandisePaidPrice)
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        merchandiseRemaining
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "i",
                                        null,
                                        currencyFormat(merchandiseRemainingPrice)
                                    )
                                )
                            )
                        ) : null,
                        React.createElement(
                            "tr",
                            { className: "finances-summary-row" },
                            React.createElement(
                                "td",
                                null,
                                React.createElement(
                                    "b",
                                    null,
                                    "Total"
                                )
                            ),
                            React.createElement("td", null),
                            React.createElement(
                                "td",
                                null,
                                React.createElement(
                                    "b",
                                    null,
                                    currencyFormat(dancersOwedPrice + merchandiseOwedPrice)
                                )
                            ),
                            React.createElement("td", null),
                            React.createElement(
                                "td",
                                null,
                                React.createElement(
                                    "b",
                                    null,
                                    currencyFormat(dancersPaidPrice + merchandisePaidPrice)
                                )
                            ),
                            React.createElement("td", null),
                            React.createElement(
                                "td",
                                null,
                                React.createElement(
                                    "b",
                                    null,
                                    currencyFormat(dancersRemainingPrice + merchandiseRemainingPrice)
                                )
                            )
                        )
                    )
                ),
                this.props.settings.view_only ? null : React.createElement(
                    React.Fragment,
                    null,
                    React.createElement(
                        "div",
                        { className: "mt-3 mb-4" },
                        React.createElement(
                            "h2",
                            null,
                            "Received by organization:"
                        ),
                        React.createElement(
                            "h4",
                            null,
                            currencyFormat(this.props.prices.team),
                            " / ",
                            currencyFormat(dancersOwedPrice + merchandiseOwedPrice)
                        )
                    ),
                    React.createElement(
                        "form",
                        { className: "my-3", method: "POST", encType: "multipart/form-data", noValidate: true },
                        React.createElement("input", { className: "btn btn-primary", id: "download_file", name: "download_file", type: "submit", value: "Download list of all payments" })
                    )
                ),
                React.createElement(
                    "table",
                    { className: "table table-sm table-hover table-finances" },
                    React.createElement(
                        "thead",
                        null,
                        React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "th",
                                { style: { width: '26%' }, className: "font-size-4" },
                                "Confirmed dancers"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' }, className: "text-right" },
                                "Entry fee"
                            ),
                            React.createElement("th", { style: { width: '8%' } }),
                            React.createElement(
                                "th",
                                { style: { width: '20%' }, className: "text-right" },
                                "Merchandise"
                            ),
                            React.createElement("th", { style: { width: '10%' } }),
                            React.createElement("th", { style: { width: '8%' } }),
                            React.createElement(
                                "th",
                                { style: { width: '10%' }, className: "text-right" },
                                "Total"
                            ),
                            React.createElement("th", { style: { width: '8%' } })
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
                                { className: "text-right" },
                                "Price"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Paid"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Item"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Price"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Paid"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Price"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Paid"
                            )
                        )
                    ),
                    React.createElement(
                        "tbody",
                        null,
                        dancers.filter(filterConfirmed).length > 0 ? dancers.filter(filterConfirmed).sort(sortDancersAlphabetically).map(function (d) {
                            return React.createElement(
                                "tr",
                                { className: d.pending ? "table-warning" : d.payment_info.all_paid ? "table-success" : d.payment_info.partial_paid ? "table-info" : "", key: 'row' + ("" + d.contestant_id) },
                                React.createElement(
                                    "td",
                                    null,
                                    d.full_name
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    currencyFormat(_this5.props.prices[d.contestant_info.student])
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    _this5.props.settings.view_only ? React.createElement("input", { type: "checkbox", disabled: true, defaultChecked: d.payment_info.entry_paid }) : React.createElement("input", { type: "checkbox", onChange: function onChange() {
                                            return _this5.entryPayment(d);
                                        }, checked: d.payment_info.entry_paid })
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(function (p) {
                                        return !p.cancelled ? React.createElement(
                                            "div",
                                            { key: 'item' + ("" + p.merchandise_purchased_id) },
                                            p.item
                                        ) : null;
                                    }) : "-"
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(function (p) {
                                        return !p.cancelled ? React.createElement(
                                            "div",
                                            { key: 'price' + ("" + p.merchandise_purchased_id) },
                                            currencyFormat(p.price)
                                        ) : null;
                                    }) : "-"
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(function (p) {
                                        return !p.cancelled ? React.createElement(
                                            "div",
                                            { key: 'paid' + ("" + p.merchandise_purchased_id) },
                                            _this5.props.settings.view_only ? React.createElement("input", { type: "checkbox", disabled: true, defaultChecked: p.paid }) : React.createElement("input", { type: "checkbox", onChange: function onChange() {
                                                    return _this5.merchandisePayment(d, p);
                                                }, checked: p.paid })
                                        ) : null;
                                    }) : "-"
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    currencyFormat(_this5.props.prices[d.contestant_info.student] + d.merchandise_info.merchandise_price)
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    _this5.props.settings.view_only ? React.createElement("input", { type: "checkbox", disabled: true, defaultChecked: d.payment_info.all_paid }) : React.createElement("input", { type: "checkbox", onChange: function onChange() {
                                            return _this5.allPayment(d);
                                        }, checked: d.payment_info.all_paid })
                                )
                            );
                        }) : React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "td",
                                { colSpan: "8" },
                                "There are no confirmed dancers with a payment requirement."
                            )
                        )
                    )
                ),
                React.createElement(
                    "table",
                    { className: "table table-sm table-hover table-finances" },
                    React.createElement(
                        "thead",
                        null,
                        React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "th",
                                { style: { width: '26%' }, className: "font-size-4" },
                                "Cancelled dancers"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' }, className: "text-right" },
                                "Entry fee"
                            ),
                            React.createElement("th", { style: { width: '8%' } }),
                            React.createElement(
                                "th",
                                { style: { width: '20%' }, className: "text-right" },
                                "Merchandise"
                            ),
                            React.createElement("th", { style: { width: '10%' } }),
                            React.createElement("th", { style: { width: '8%' } }),
                            React.createElement(
                                "th",
                                { style: { width: '10%' }, className: "text-right" },
                                "Total"
                            ),
                            React.createElement("th", { style: { width: '8%' } })
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
                                { className: "text-right" },
                                "Price"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Paid"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Item"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Price"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Paid"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Price"
                            ),
                            React.createElement(
                                "th",
                                { className: "text-right" },
                                "Paid"
                            )
                        )
                    ),
                    React.createElement(
                        "tbody",
                        null,
                        dancers.filter(filterCancelled).length > 0 ? dancers.filter(filterCancelled).sort(sortDancersAlphabetically).map(function (d) {
                            return React.createElement(
                                "tr",
                                { className: d.pending ? "table-warning" : d.payment_info.all_paid ? "table-success" : d.payment_info.partial_paid ? "table-info" : "", key: 'row' + ("" + d.contestant_id) },
                                React.createElement(
                                    "td",
                                    null,
                                    d.full_name
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    currencyFormat(_this5.props.prices[d.contestant_info.student])
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    _this5.props.settings.view_only ? React.createElement("input", { type: "checkbox", disabled: true, defaultChecked: d.payment_info.entry_paid }) : React.createElement("input", { type: "checkbox", onChange: function onChange() {
                                            return _this5.entryPayment(d);
                                        }, checked: d.payment_info.entry_paid })
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
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
                                    { className: "text-right" },
                                    Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(function (p) {
                                        return React.createElement(
                                            "div",
                                            { key: 'price' + ("" + p.merchandise_purchased_id) },
                                            currencyFormat(p.price)
                                        );
                                    }) : "-"
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(function (p) {
                                        return React.createElement(
                                            "div",
                                            { key: 'paid' + ("" + p.merchandise_purchased_id) },
                                            _this5.props.settings.view_only ? React.createElement("input", { type: "checkbox", disabled: true, defaultChecked: p.paid }) : React.createElement("input", { type: "checkbox", onChange: function onChange() {
                                                    return _this5.merchandisePayment(d, p);
                                                }, checked: p.paid })
                                        );
                                    }) : "-"
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    currencyFormat(_this5.props.prices[d.contestant_info.student] + d.merchandise_info.merchandise_price)
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    _this5.props.settings.view_only ? React.createElement("input", { type: "checkbox", disabled: true, defaultChecked: d.payment_info.all_paid }) : React.createElement("input", { type: "checkbox", onChange: function onChange() {
                                            return _this5.allPayment(d);
                                        }, checked: d.payment_info.all_paid })
                                )
                            );
                        }) : React.createElement(
                            "tr",
                            null,
                            React.createElement(
                                "td",
                                { colSpan: "8" },
                                "There are no dancers that have cancelled with a payment requirement."
                            )
                        )
                    )
                ),
                dancers.filter(filterHasRefund).length > 0 ? React.createElement(
                    "table",
                    { className: "table table-sm table-finances mt-3" },
                    React.createElement(
                        "thead",
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
                                { style: { width: '32%' } },
                                "Dancer"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '50%' } },
                                "Refund reason(s)"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: '10%' }, className: "text-right" },
                                "Refund"
                            ),
                            React.createElement("th", { style: { width: '8%' } })
                        )
                    ),
                    React.createElement(
                        "tbody",
                        null,
                        dancers.filter(filterHasRefund).sort(sortDancersAlphabetically).map(function (d) {
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
                                React.createElement("td", null)
                            );
                        })
                    )
                ) : null
            );
        }
    }]);

    return TeamCaptainFinances;
}(React.Component);