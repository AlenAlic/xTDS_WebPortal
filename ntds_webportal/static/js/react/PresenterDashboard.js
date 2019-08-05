var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var maxTabs = 3;

var PresenterDashboard = function (_React$Component) {
    _inherits(PresenterDashboard, _React$Component);

    function PresenterDashboard(props) {
        _classCallCheck(this, PresenterDashboard);

        var _this = _possibleConstructorReturn(this, (PresenterDashboard.__proto__ || Object.getPrototypeOf(PresenterDashboard)).call(this, props));

        _this.state = {
            competitions: [],
            windows: []
        };
        return _this;
    }

    _createClass(PresenterDashboard, [{
        key: "componentDidMount",
        value: function componentDidMount() {
            this.getCompetitions();
        }
    }, {
        key: "getCompetitions",
        value: function getCompetitions() {
            var _this2 = this;

            fetch("/adjudication_system/api/presenter/competition_list", { method: "GET", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                result = Object.values(result).sort(function (a, b) {
                    return b.date - a.date;
                });
                _this2.setState({ competitions: result });
            });
        }
    }, {
        key: "getCompetitionsRounds",
        value: function getCompetitionsRounds(id) {
            var _this3 = this;

            fetch("/adjudication_system/api/presenter/competition_heat_list/" + id, { method: "GET", credentials: 'same-origin' }).then(function (response) {
                return response.json();
            }).then(function (result) {
                result = Object.values(result).sort(function (a, b) {
                    return b.date - a.date;
                });
                _this3.setState({ competitions: result });
            });
        }
    }, {
        key: "numberOfTabs",
        value: function numberOfTabs(event) {
            this.setState({ tabs: Number(event.target.value) });
        }
    }, {
        key: "addCompetition",
        value: function addCompetition(event, id) {
            var newWindows = this.state.windows;
            var competition = this.state.competitions.find(function (c) {
                return c.id === id;
            });
            if (!newWindows.includes(competition) && newWindows.length < maxTabs) {
                if (newWindows.length === maxTabs) {
                    newWindows.shift();
                }
                newWindows.push(competition);
            } else {
                newWindows = newWindows.filter(function (v) {
                    return v !== competition;
                });
            }
            this.setState({ windows: newWindows });
        }
    }, {
        key: "render",
        value: function render() {
            var _this4 = this;

            var competitions = this.state.competitions;
            var windows = this.state.windows;

            return React.createElement(
                React.Fragment,
                null,
                React.createElement(
                    "h2",
                    null,
                    "Add competitions to overview"
                ),
                React.createElement(
                    "div",
                    { className: "d-flex justify-content-between flex-wrap mb-3" },
                    competitions.map(function (c) {
                        return React.createElement(
                            "div",
                            { className: "form-group form-check mx-3", key: "competition-checkbox-" + c.id },
                            React.createElement("input", { type: "checkbox", className: "form-check-input", id: "competition-checkbox-" + c.id,
                                value: c.id, onChange: function onChange(e) {
                                    return _this4.addCompetition(e, c.id);
                                }, disabled: windows.length === maxTabs && !windows.includes(c) }),
                            React.createElement(
                                "label",
                                { className: "form-check-label clickable", htmlFor: "competition-checkbox-" + c.id },
                                c.name
                            )
                        );
                    })
                ),
                React.createElement(
                    "div",
                    { className: "d-grid grid-column-gap-2 grid-template-columns-" + windows.length },
                    windows.map(function (c) {
                        return React.createElement(
                            PresenterWindow,
                            { key: "competition-title-" + c.id, competition: c },
                            c.name
                        );
                    })
                )
            );
        }
    }]);

    return PresenterDashboard;
}(React.Component);