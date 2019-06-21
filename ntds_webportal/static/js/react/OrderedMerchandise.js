var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var OrderedMerchandise = function (_React$Component) {
    _inherits(OrderedMerchandise, _React$Component);

    function OrderedMerchandise(props) {
        _classCallCheck(this, OrderedMerchandise);

        var _this = _possibleConstructorReturn(this, (OrderedMerchandise.__proto__ || Object.getPrototypeOf(OrderedMerchandise)).call(this, props));

        _this.state = { dancers: _this.props.dancers };
        return _this;
    }

    _createClass(OrderedMerchandise, [{
        key: "setPending",
        value: function setPending(dancer) {
            var newState = this.state.dancers;
            dancer.pending = true;
            newState[dancer.contestant_id] = dancer;
            this.setState({ dancers: newState });
        }
    }, {
        key: "itemOrdered",
        value: function itemOrdered(dancer, purchase) {
            var _this2 = this;

            this.setPending(dancer);
            var newState = this.state.dancers;
            fetch("/api/contestants/" + dancer.contestant_id + "/purchase_ordered/" + purchase.merchandise_purchased_id + "/" + Number(!purchase.ordered), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
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
        key: "render",
        value: function render() {
            var _this3 = this;

            var dancers = Object.values(this.state.dancers).sort(sortDancersAlphabetically);

            return React.createElement(
                "div",
                { className: "panel-group page-break", id: "merchandise-dancers" },
                React.createElement(
                    "div",
                    { className: "card" },
                    React.createElement(
                        "div",
                        { className: "card-header clickable", role: "button", id: "headingOne", "data-toggle": "collapse",
                            "data-parent": "#merchandise-dancers", href: "#collapseOne" },
                        "Dancers that have purchased merchandise ",
                        React.createElement(
                            "span",
                            { className: "badge badge-pill badge-dark" },
                            dancers.length
                        )
                    ),
                    React.createElement(
                        "div",
                        { id: "collapseOne", className: "collapse show card-body px-0 py-0" },
                        dancers.length > 0 ? React.createElement(
                            "table",
                            { className: "table table-sm mb-0" },
                            React.createElement(
                                "thead",
                                null,
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
                                        "Email"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' } },
                                        "Team"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '20%' } },
                                        "Item"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '8%' } },
                                        "Ordered"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '5%' } },
                                        "Paid"
                                    ),
                                    React.createElement(
                                        "th",
                                        { style: { width: '7%' } },
                                        "Received"
                                    )
                                )
                            ),
                            React.createElement(
                                "tbody",
                                null,
                                dancers.map(function (d) {
                                    return Object.values(d.merchandise_info.purchases).filter(filterPurchaseNotCancelled).map(function (p, i) {
                                        return React.createElement(
                                            "tr",
                                            { className: d.pending ? "table-warning" : p.ordered && p.paid && p.received ? "table-success" : null, key: "row-" + d.contestant_id },
                                            i === 0 ? React.createElement(
                                                React.Fragment,
                                                null,
                                                React.createElement(
                                                    "td",
                                                    null,
                                                    d.full_name
                                                ),
                                                React.createElement(
                                                    "td",
                                                    null,
                                                    d.email
                                                ),
                                                React.createElement(
                                                    "td",
                                                    null,
                                                    d.contestant_info.team
                                                )
                                            ) : React.createElement("td", { colSpan: "3" }),
                                            React.createElement(
                                                "td",
                                                null,
                                                p.item
                                            ),
                                            React.createElement(
                                                "td",
                                                null,
                                                React.createElement("input", { type: "checkbox", onChange: function onChange() {
                                                        return _this3.itemOrdered(d, p);
                                                    }, checked: p.ordered })
                                            ),
                                            React.createElement(
                                                "td",
                                                null,
                                                React.createElement(CheckMark, { flag: p.paid })
                                            ),
                                            React.createElement(
                                                "td",
                                                null,
                                                React.createElement(CheckMark, { flag: p.received })
                                            )
                                        );
                                    });
                                })
                            )
                        ) : React.createElement(
                            "p",
                            null,
                            "There are no dancers that have orderd merchandise"
                        )
                    )
                )
            );
        }
    }]);

    return OrderedMerchandise;
}(React.Component);