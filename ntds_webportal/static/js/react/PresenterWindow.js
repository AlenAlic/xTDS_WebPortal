var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var PresenterAccordionCard = function (_React$Component) {
    _inherits(PresenterAccordionCard, _React$Component);

    function PresenterAccordionCard(props) {
        _classCallCheck(this, PresenterAccordionCard);

        var _this = _possibleConstructorReturn(this, (PresenterAccordionCard.__proto__ || Object.getPrototypeOf(PresenterAccordionCard)).call(this, props));

        _this.state = { collapsed: true };

        _this.toggle = _this.toggle.bind(_this);
        return _this;
    }

    _createClass(PresenterAccordionCard, [{
        key: "toggle",
        value: function toggle() {
            this.setState({ collapsed: !this.state.collapsed });
        }
    }, {
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "card mb-0" },
                React.createElement(
                    "div",
                    { className: "card-header" },
                    React.createElement(
                        "span",
                        null,
                        this.props.cardTitle
                    ),
                    this.props.counter ? React.createElement(
                        "span",
                        { className: "badge mx-2 " + (this.props.counter.x === this.props.counter.total ? "badge-success" : "badge-dark") },
                        this.props.counter.x,
                        " / ",
                        this.props.counter.total
                    ) : null,
                    this.props.loading ? React.createElement("span", { className: "spinner-border spinner-border-sm mx-2", role: "status" }) : null,
                    React.createElement(
                        "span",
                        { className: "float-right " + (this.state.collapsed ? "collapsed" : "") + " clickable", onClick: this.toggle },
                        React.createElement(
                            "span",
                            { className: "border border-dark rounded px-3 py-1" },
                            this.state.collapsed ? React.createElement("i", { className: "fas fa-chevron-circle-down" }) : React.createElement("i", { className: "fas fa-chevron-circle-up" })
                        )
                    )
                ),
                React.createElement(
                    "div",
                    { className: "collapse " + (this.state.collapsed ? "" : "show"), "data-parent": "#" + this.props.accordion },
                    React.createElement(
                        "div",
                        { className: "card-body" },
                        this.props.children
                    )
                )
            );
        }
    }]);

    return PresenterAccordionCard;
}(React.Component);

var QUALIFICATION = "qualification";
var GENERAL_LOOK = "general_look";
var FIRST_ROUND = "first_round";
var SECOND_ROUND = "second_round";
var RE_DANCE = "re_dance";
var INTERMEDIATE_ROUND = "intermediate_round";
var EIGHT_FINAL = "eight_final";
var QUARTER_FINAL = "quarter_final";
var SEMI_FINAL = "semi_final";
var FINAL = "final";
var updatePresentCouples = [QUALIFICATION, GENERAL_LOOK, FIRST_ROUND, SECOND_ROUND, RE_DANCE, INTERMEDIATE_ROUND, EIGHT_FINAL, QUARTER_FINAL, SEMI_FINAL];
var dontUpdatePresentCouples = [FINAL];

var CHANGE_PER_ROUND = "change_per_round";
var CHANGE_PER_DANCE = "change_per_dance";
var CHANGE_MODES = [CHANGE_PER_ROUND, CHANGE_PER_DANCE];

var StartingList = function StartingList(_ref) {
    var startingList = _ref.startingList,
        selectedRound = _ref.selectedRound;

    return startingList.map(function (d) {
        return React.createElement(
            "div",
            { key: "number-" + d.number },
            React.createElement(
                "b",
                null,
                d.number
            ),
            " - ",
            d.name,
            selectedRound.type === FINAL ? " (" + d.team + ")" : null
        );
    });
};
var DancersList = function DancersList(_ref2) {
    var list = _ref2.list,
        selectedRound = _ref2.selectedRound;

    return CHANGE_MODES.includes(selectedRound.mode) ? React.createElement(
        "div",
        { className: "d-grid grid-template-columns-2 grid-column-gap-2" },
        React.createElement(
            "div",
            null,
            React.createElement(
                "h4",
                null,
                "Leads"
            ),
            React.createElement(StartingList, { startingList: list.leads, selectedRound: selectedRound })
        ),
        React.createElement(
            "div",
            null,
            React.createElement(
                "h4",
                null,
                "Follows"
            ),
            React.createElement(StartingList, { startingList: list.follows, selectedRound: selectedRound })
        )
    ) : React.createElement(
        "div",
        null,
        React.createElement(StartingList, { startingList: list, selectedRound: selectedRound })
    );
};

var FinalPlacingsCouples = function FinalPlacingsCouples(_ref3) {
    var couples = _ref3.couples;

    return React.createElement(
        "div",
        { className: "d-flex justify-content-around mb-3" },
        React.createElement(
            "table",
            { className: "table table-sm" },
            React.createElement(
                "thead",
                null,
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        null,
                        "Place"
                    ),
                    React.createElement(
                        "th",
                        null,
                        "#"
                    ),
                    React.createElement(
                        "th",
                        null,
                        "Lead"
                    ),
                    React.createElement(
                        "th",
                        null,
                        "Follow"
                    ),
                    React.createElement(
                        "th",
                        null,
                        "Team(s)"
                    )
                )
            ),
            React.createElement(
                "tbody",
                null,
                couples.map(function (c) {
                    return React.createElement(
                        "tr",
                        { key: "place-" + c.place },
                        React.createElement(
                            "td",
                            null,
                            c.place
                        ),
                        React.createElement(
                            "td",
                            null,
                            c.number
                        ),
                        React.createElement(
                            "td",
                            null,
                            c.lead
                        ),
                        React.createElement(
                            "td",
                            null,
                            c.follow
                        ),
                        React.createElement(
                            "td",
                            null,
                            c.team
                        )
                    );
                })
            )
        )
    );
};
var FinalPlacingsDancers = function FinalPlacingsDancers(_ref4) {
    var dancers = _ref4.dancers;

    return React.createElement(
        "div",
        { className: "d-flex justify-content-around mb-3" },
        React.createElement(
            "table",
            { className: "table table-sm" },
            React.createElement(
                "thead",
                null,
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        null,
                        "Place"
                    ),
                    React.createElement(
                        "th",
                        null,
                        "#"
                    ),
                    React.createElement(
                        "th",
                        null,
                        "Name"
                    ),
                    React.createElement(
                        "th",
                        null,
                        "Team"
                    )
                )
            ),
            React.createElement(
                "tbody",
                null,
                dancers.map(function (d) {
                    return React.createElement(
                        "tr",
                        { key: "place-" + d.place },
                        React.createElement(
                            "td",
                            null,
                            d.place
                        ),
                        React.createElement(
                            "td",
                            null,
                            d.number
                        ),
                        React.createElement(
                            "td",
                            null,
                            d.name
                        ),
                        React.createElement(
                            "td",
                            null,
                            d.team
                        )
                    );
                })
            )
        )
    );
};
var SkatingSummary = function SkatingSummary(_ref5) {
    var finalResult = _ref5.finalResult;

    return React.createElement(
        "table",
        { className: "table-sm table-skating print-friendly text-center mb-4" },
        React.createElement(
            "thead",
            null,
            React.createElement(
                "tr",
                null,
                React.createElement(
                    "th",
                    { colSpan: finalResult.dances.length + 3 },
                    "Final Summary"
                )
            ),
            React.createElement(
                "tr",
                null,
                React.createElement(
                    "th",
                    { rowSpan: "2", className: "align-bottom" },
                    "No."
                ),
                React.createElement(
                    "th",
                    { colSpan: finalResult.dances.length },
                    "Dances"
                ),
                React.createElement(
                    "th",
                    { rowSpan: "2", className: "align-bottom" },
                    "Tot."
                ),
                React.createElement(
                    "th",
                    { rowSpan: "2", className: "align-bottom" },
                    "Res."
                )
            ),
            React.createElement(
                "tr",
                null,
                finalResult.dances.map(function (d) {
                    return React.createElement(
                        "th",
                        { key: "dance-" + d },
                        d
                    );
                })
            )
        ),
        React.createElement(
            "tbody",
            null,
            finalResult.rows.map(function (r, i) {
                return React.createElement(
                    "tr",
                    { key: "row-" + i },
                    r.map(function (c, j) {
                        return React.createElement(
                            "td",
                            { key: "column-" + j },
                            c
                        );
                    })
                );
            })
        )
    );
};
var SkatingRule = function SkatingRule(_ref6) {
    var rule = _ref6.rule,
        ruleText = _ref6.ruleText,
        places = _ref6.places;

    return React.createElement(
        "table",
        { className: "table-sm table-skating text-center mb-2" },
        React.createElement(
            "thead",
            null,
            React.createElement(
                "tr",
                null,
                React.createElement(
                    "th",
                    { rowSpan: "2", className: "align-bottom" },
                    "No."
                ),
                React.createElement(
                    "th",
                    { colSpan: places.length },
                    ruleText
                ),
                React.createElement(
                    "th",
                    { rowSpan: "2", className: "align-bottom" },
                    "Res."
                )
            ),
            React.createElement(
                "tr",
                null,
                places.map(function (c, i) {
                    return React.createElement(
                        "th",
                        { key: "column-" + i },
                        1,
                        i > 0 ? "-" + (i + 1) : ""
                    );
                })
            )
        ),
        React.createElement(
            "tbody",
            null,
            rule.rows.map(function (r, i) {
                return React.createElement(
                    "tr",
                    { key: "row-" + i },
                    r.map(function (c, j) {
                        return React.createElement(
                            "td",
                            { key: "column-" + j },
                            c
                        );
                    })
                );
            })
        )
    );
};

var UPDATE_INTERVAL = 3000;

var PresenterWindow = function (_React$Component2) {
    _inherits(PresenterWindow, _React$Component2);

    function PresenterWindow(props) {
        _classCallCheck(this, PresenterWindow);

        var _this2 = _possibleConstructorReturn(this, (PresenterWindow.__proto__ || Object.getPrototypeOf(PresenterWindow)).call(this, props));

        _this2.state = {
            rounds: [],
            selectedRound: null,
            noRounds: false,

            adjudicators: null,
            loadingAdjudicators: false,
            updateAdjudicators: false,

            startingList: null,
            loadingStartingList: false,

            couplesPresent: null,
            loadingCouplesPresent: false,
            updateCouplesPresent: false,

            noReDanceList: null,
            loadingNoReDanceList: false,

            finalResult: null,
            loadingFinalResult: false
        };
        _this2.changeRound = _this2.changeRound.bind(_this2);
        _this2.refresh = _this2.refresh.bind(_this2);

        _this2.controller = new AbortController();
        _this2.signal = _this2.controller.signal;
        return _this2;
    }

    _createClass(PresenterWindow, [{
        key: "componentDidMount",
        value: function componentDidMount() {
            var _this3 = this;

            this.getRounds(true);
            this.intervalCouplesPresent = setInterval(function () {
                _this3.state.selectedRound !== null && !_this3.state.selectedRound.completed && _this3.state.updateCouplesPresent ? _this3.getCouplesPresent(_this3.state.selectedRound.id) : null;
            }, UPDATE_INTERVAL);
            this.intervalAdjudicators = setInterval(function () {
                _this3.state.selectedRound !== null && !_this3.state.selectedRound.completed && _this3.state.adjudicators !== null && _this3.state.updateAdjudicators ? _this3.getAdjudicators(_this3.state.selectedRound.id) : null;
            }, UPDATE_INTERVAL);
        }
    }, {
        key: "componentWillUnmount",
        value: function componentWillUnmount() {
            clearInterval(this.intervalCouplesPresent);
            clearInterval(this.intervalAdjudicators);
            this.controller.abort();
        }
    }, {
        key: "getRounds",
        value: function getRounds() {
            var _this4 = this;

            var changeRound = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;

            fetch("/adjudication_system/api/presenter/competition/" + this.props.competition.id + "/rounds", { method: "GET", credentials: 'same-origin', signal: this.signal }).then(function (response) {
                return response.json();
            }).then(function (result) {
                _this4.setState({ noRounds: result.length === 0 });
                if (changeRound) {
                    var selectedRound = result.reduce(function (p, c) {
                        return p.id > c.id ? p : c;
                    });
                    _this4.setState({ rounds: result, selectedRound: selectedRound });
                    _this4.setData(selectedRound);
                } else {
                    _this4.setState({ rounds: result });
                    _this4.setData(_this4.state.selectedRound);
                }
            }).catch(function () {});
        }
    }, {
        key: "changeRound",
        value: function changeRound(event) {
            var selectedRound = this.state.rounds.find(function (r) {
                return r.id === Number(event.target.value);
            });
            this.setState({ selectedRound: selectedRound });
            this.setData(selectedRound);
        }
    }, {
        key: "setData",
        value: function setData(selectedRound) {
            this.getCouplesPresent(selectedRound.id);
            this.getStartingList(selectedRound.id);
            this.getAdjudicators(selectedRound.id);
            {
                selectedRound.type === RE_DANCE ? this.getNoReDanceCouples(selectedRound.id) : null;
            }
            {
                selectedRound.type === FINAL ? this.getFinalResult(selectedRound.id) : null;
            }
        }
    }, {
        key: "refresh",
        value: function refresh() {
            this.getRounds();
        }
    }, {
        key: "getAdjudicators",
        value: function getAdjudicators(id) {
            var _this5 = this;

            this.setState({ loadingAdjudicators: true });
            fetch("/adjudication_system/api/presenter/round/" + id + "/adjudicators", { method: "GET", credentials: 'same-origin', signal: this.signal }).then(function (response) {
                return response.json();
            }).then(function (result) {
                _this5.setState({
                    adjudicators: result,
                    loadingAdjudicators: false,
                    updateAdjudicators: result.map(function (a) {
                        return a.present;
                    }).includes(false)
                });
            }).catch(function () {
                _this5.setState({ loadingAdjudicators: false });
            });
        }
    }, {
        key: "getStartingList",
        value: function getStartingList(id) {
            var _this6 = this;

            this.setState({ loadingStartingList: true });
            fetch("/adjudication_system/api/presenter/round/" + id + "/starting_list", { method: "GET", credentials: 'same-origin', signal: this.signal }).then(function (response) {
                return response.json();
            }).then(function (result) {
                _this6.setState({ startingList: result, loadingStartingList: false });
            }).catch(function () {
                _this6.setState({ loadingStartingList: false });
            });
        }
    }, {
        key: "getCouplesPresent",
        value: function getCouplesPresent(id) {
            var _this7 = this;

            this.setState({ loadingCouplesPresent: true });
            fetch("/adjudication_system/api/presenter/round/" + id + "/couples_present", { method: "GET", credentials: 'same-origin', signal: this.signal }).then(function (response) {
                return response.json();
            }).then(function (result) {
                _this7.setState({
                    couplesPresent: result.sort(function (a, b) {
                        return a.order - b.order;
                    }),
                    updateCouplesPresent: _this7.state.selectedRound.type !== "final",
                    loadingCouplesPresent: false
                });
            }).catch(function () {
                _this7.setState({ loadingCouplesPresent: false });
            });
        }
    }, {
        key: "getNoReDanceCouples",
        value: function getNoReDanceCouples(id) {
            var _this8 = this;

            this.setState({ loadingNoReDanceList: true });
            fetch("/adjudication_system/api/presenter/round/" + id + "/no_redance_couples", { method: "GET", credentials: 'same-origin', signal: this.signal }).then(function (response) {
                return response.json();
            }).then(function (result) {
                _this8.setState({ noReDanceList: result, loadingNoReDanceList: false });
            }).catch(function () {
                _this8.setState({ loadingNoReDanceList: false });
            });
        }
    }, {
        key: "getFinalResult",
        value: function getFinalResult(id) {
            var _this9 = this;

            this.setState({ loadingFinalResult: true });
            fetch("/adjudication_system/api/presenter/round/" + id + "/final_results", { method: "GET", credentials: 'same-origin', signal: this.signal }).then(function (response) {
                return response.json();
            }).then(function (result) {
                _this9.setState({ finalResult: result, loadingFinalResult: false });
            }).catch(function () {
                _this9.setState({ loadingFinalResult: false });
            });
        }
    }, {
        key: "render",
        value: function render() {
            var rounds = this.state.rounds;
            var selectedRound = this.state.selectedRound;

            var adjudicators = this.state.adjudicators;
            var startingList = this.state.startingList;
            var couplesPresent = this.state.couplesPresent;
            var noReDanceList = this.state.noReDanceList;
            var finalResult = this.state.finalResult;

            return React.createElement(
                React.Fragment,
                null,
                this.state.noRounds && React.createElement(
                    "h3",
                    { className: "text-center" },
                    "There are no rounds yet for ",
                    this.props.competition.name
                ),
                selectedRound !== null && React.createElement(
                    "div",
                    { className: "card" },
                    React.createElement(
                        "div",
                        { className: "px-2 py-2" },
                        React.createElement(
                            "h4",
                            { className: "card-title" },
                            this.props.competition.name
                        ),
                        React.createElement(
                            "div",
                            { className: "form-group" },
                            React.createElement(
                                "label",
                                { htmlFor: "round-" + this.props.competition.id },
                                "Select round"
                            ),
                            React.createElement(
                                "select",
                                { className: "form-control", id: "round-" + this.props.competition.id, value: selectedRound.id, onChange: this.changeRound },
                                rounds.map(function (r) {
                                    return React.createElement(
                                        "option",
                                        { value: r.id, key: "round-option-" + r.id },
                                        r.name
                                    );
                                })
                            ),
                            React.createElement(
                                "div",
                                { className: "text-center mt-3" },
                                React.createElement(
                                    "button",
                                    { className: "btn btn-dark", onClick: this.refresh },
                                    "Refresh"
                                )
                            )
                        )
                    ),
                    React.createElement(
                        "div",
                        { className: "px-2 pb-2" },
                        selectedRound !== null && React.createElement(
                            "div",
                            { className: "accordion", id: "accordion-" + selectedRound.id },
                            selectedRound.type === FINAL && this.state.selectedRound.completed && React.createElement(
                                PresenterAccordionCard,
                                { accordion: "accordion-" + selectedRound.id, cardTitle: "Final results", loading: this.state.loadingFinalResult },
                                finalResult !== null && (!finalResult.separate ? React.createElement(
                                    React.Fragment,
                                    null,
                                    React.createElement(FinalPlacingsCouples, { couples: finalResult.couples }),
                                    React.createElement(SkatingSummary, { finalResult: finalResult }),
                                    finalResult.show_rules && React.createElement(
                                        React.Fragment,
                                        null,
                                        React.createElement(SkatingRule, { ruleText: "Rule 10", places: finalResult.couples, rule: finalResult.rule10 }),
                                        React.createElement(SkatingRule, { ruleText: "Rule 11", places: finalResult.couples, rule: finalResult.rule11 })
                                    )
                                ) : React.createElement(
                                    "div",
                                    { className: "d-grid grid-column-gap-3 grid-row-gap-4 grid-template-columns-" + (this.props.windows < 3 ? "2" : "1") },
                                    React.createElement(
                                        "div",
                                        null,
                                        React.createElement(
                                            "h3",
                                            { className: "text-center" },
                                            "Leads"
                                        ),
                                        React.createElement(FinalPlacingsDancers, { dancers: finalResult.leads.dancers }),
                                        React.createElement(SkatingSummary, { finalResult: finalResult.leads }),
                                        finalResult.leads.show_rules && React.createElement(
                                            React.Fragment,
                                            null,
                                            React.createElement(SkatingRule, { ruleText: "Rule 10", places: finalResult.leads.dancers, rule: finalResult.leads.rule10 }),
                                            React.createElement(SkatingRule, { ruleText: "Rule 11", places: finalResult.leads.dancers, rule: finalResult.leads.rule11 })
                                        )
                                    ),
                                    React.createElement(
                                        "div",
                                        null,
                                        React.createElement(
                                            "h3",
                                            { className: "text-center" },
                                            "Follows"
                                        ),
                                        React.createElement(FinalPlacingsDancers, { dancers: finalResult.follows.dancers }),
                                        React.createElement(SkatingSummary, { finalResult: finalResult.follows }),
                                        finalResult.follows.show_rules && React.createElement(
                                            React.Fragment,
                                            null,
                                            React.createElement(SkatingRule, { ruleText: "Rule 10", places: finalResult.follows.dancers, rule: finalResult.follows.rule10 }),
                                            React.createElement(SkatingRule, { ruleText: "Rule 11", places: finalResult.follows.dancers, rule: finalResult.follows.rule11 })
                                        )
                                    )
                                ))
                            ),
                            React.createElement(
                                PresenterAccordionCard,
                                { accordion: "accordion-" + selectedRound.id, cardTitle: "Adjudicators", loading: this.state.loadingAdjudicators, counter: adjudicators !== null ? { "x": adjudicators.filter(function (a) {
                                            return a.present === true;
                                        }).length, "total": adjudicators.length } : adjudicators },
                                React.createElement(
                                    "div",
                                    null,
                                    adjudicators !== null && adjudicators.map(function (a) {
                                        return React.createElement(
                                            "div",
                                            { key: "adjudicator-" + a.id },
                                            React.createElement(
                                                "span",
                                                { className: a.present ? "text-success" : "text-danger" },
                                                a.name
                                            ),
                                            !a.present ? " (" + a.round + ")" : null
                                        );
                                    })
                                )
                            ),
                            React.createElement(
                                PresenterAccordionCard,
                                { accordion: "accordion-" + selectedRound.id, cardTitle: "Starting list", loading: this.state.loadingStartingList },
                                startingList !== null && React.createElement(DancersList, { list: startingList, selectedRound: selectedRound })
                            ),
                            selectedRound.type === RE_DANCE && React.createElement(
                                PresenterAccordionCard,
                                { accordion: "accordion-" + selectedRound.id, cardTitle: "No re-dance", loading: this.state.loadingNoReDanceList },
                                noReDanceList !== null && React.createElement(DancersList, { list: noReDanceList, selectedRound: selectedRound })
                            ),
                            !dontUpdatePresentCouples.includes(selectedRound.type) && React.createElement(
                                PresenterAccordionCard,
                                { accordion: "accordion-" + selectedRound.id, cardTitle: "Couples present", loading: this.state.loadingCouplesPresent },
                                React.createElement(
                                    "div",
                                    null,
                                    couplesPresent !== null && couplesPresent.map(function (d) {
                                        return React.createElement(
                                            React.Fragment,
                                            { key: "dance-" + d.id },
                                            React.createElement(
                                                "h5",
                                                null,
                                                d.name
                                            ),
                                            React.createElement(
                                                "div",
                                                { className: "mb-3" },
                                                d.heats.map(function (h) {
                                                    return React.createElement(
                                                        React.Fragment,
                                                        { key: "heat-" + h.id },
                                                        React.createElement(
                                                            "h6",
                                                            null,
                                                            "Heat ",
                                                            h.number
                                                        ),
                                                        React.createElement(
                                                            "div",
                                                            null,
                                                            h.couples.map(function (c) {
                                                                return React.createElement(
                                                                    "b",
                                                                    { key: "couple-" + c.number, className: "px-3 d-inline-block text-nowrap " + (c.present ? "text-success" : "text-danger") },
                                                                    c.number
                                                                );
                                                            })
                                                        )
                                                    );
                                                })
                                            )
                                        );
                                    })
                                )
                            )
                        )
                    )
                )
            );
        }
    }]);

    return PresenterWindow;
}(React.Component);