var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var ActivateTeamcaptains = function (_React$Component) {
    _inherits(ActivateTeamcaptains, _React$Component);

    function ActivateTeamcaptains(props) {
        _classCallCheck(this, ActivateTeamcaptains);

        var _this = _possibleConstructorReturn(this, (ActivateTeamcaptains.__proto__ || Object.getPrototypeOf(ActivateTeamcaptains)).call(this, props));

        _this.state = { users: _this.props.users };
        return _this;
    }

    _createClass(ActivateTeamcaptains, [{
        key: "setPending",
        value: function setPending(u) {
            u.pending = true;
            var newState = this.state.users;
            newState[u.user_id] = u;
            this.setState({ user: newState });
        }
    }, {
        key: "updateEmail",
        value: function updateEmail(event, user_id) {
            var newState = this.state.users;
            newState[user_id].email = event.target.value;
            this.setState({ user: newState });
        }
    }, {
        key: "setEmail",
        value: function setEmail(u) {
            var _this2 = this;

            if (validateEmail(u.old_email) || u.email === "") {
                this.setPending(u);
                var newState = this.state.users;
                fetch("/api/users/" + u.user_id + "/set_email", { method: "PATCH", credentials: 'same-origin', body: JSON.stringify(u) }).then(function (response) {
                    return response.json();
                }).then(function (result) {
                    newState[result.user_id] = result;
                    _this2.setState({ user: newState });
                }).catch(function (error) {
                    console.log('Error: \n', error);
                    u.pending = false;
                    newState[u.user_id] = u;
                    _this2.setState({ user: newState });
                });
            } else {
                alert("Please enter a valid e-mail address.");
            }
        }
    }, {
        key: "activateUser",
        value: function activateUser(u) {
            var _this3 = this;

            if (validateEmail(u.old_email)) {
                this.setPending(u);
                var newState = this.state.users;
                fetch("/api/users/" + u.user_id + "/activate/" + Number(!u.activate), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                    return response.json();
                }).then(function (result) {
                    newState[result.user_id] = result;
                    _this3.setState({ user: newState });
                }).catch(function (error) {
                    console.log('Error: \n', error);
                    u.pending = false;
                    newState[u.user_id] = u;
                    _this3.setState({ user: newState });
                });
            } else {
                alert("Please save a valid e-mail address, before you activate the teamcaptain.");
            }
        }
    }, {
        key: "activateTeamcaptain",
        value: function activateTeamcaptain(u) {
            var _this4 = this;

            if (validateEmail(u.old_email)) {
                this.setPending(u);
                var newState = this.state.users;
                fetch("/api/users/" + u.user_id + "/activate_teamcaptain/" + Number(!u.is_active), { method: "PATCH", credentials: 'same-origin' }).then(function (response) {
                    return response.json();
                }).then(function (result) {
                    newState[result.user_id] = result;
                    _this4.setState({ user: newState });
                }).catch(function (error) {
                    console.log('Error: \n', error);
                    u.pending = false;
                    newState[u.user_id] = u;
                    _this4.setState({ user: newState });
                });
            } else {
                alert("Please save a valid e-mail address, before you activate the teamcaptain.");
            }
        }
    }, {
        key: "render",
        value: function render() {
            var _this5 = this;

            var users = Object.values(this.state.users);
            var teamcaptains = users.filter(filterUserIsTeamcaptain);
            var activateTeamcaptains = teamcaptains.filter(filterUserActivate);
            var activeTeamcaptains = teamcaptains.filter(filterUserIsActive);
            var treasurers = users.filter(filterUserIsTreasurer);
            var activeTreasurers = treasurers.filter(filterUserIsActive);

            return React.createElement(
                React.Fragment,
                null,
                this.props.settings.website_accessible_to_teamcaptains ? React.createElement(
                    "h2",
                    null,
                    "Active Teamcaptains ",
                    React.createElement(
                        "span",
                        { className: "badge badge-pill badge-dark" },
                        activeTeamcaptains.length,
                        " / ",
                        teamcaptains.length
                    ),
                    this.props.settings.website_accessible_to_teamcaptains ? React.createElement(
                        "span",
                        null,
                        " and Treasurers ",
                        React.createElement(
                            "span",
                            { className: "badge badge-pill badge-dark" },
                            activeTreasurers.length,
                            " / ",
                            treasurers.length
                        )
                    ) : null
                ) : React.createElement(
                    "h2",
                    null,
                    "Activate Teamcaptains ",
                    React.createElement(
                        "span",
                        { className: "badge badge-pill badge-dark" },
                        activateTeamcaptains.length,
                        " / ",
                        teamcaptains.length
                    )
                ),
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
                                { style: { width: "20%" } },
                                "Username"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: "15%" } },
                                "Team"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: "25%" } },
                                "E-mail"
                            ),
                            React.createElement("th", { style: { width: "15%" } }),
                            React.createElement(
                                "th",
                                { style: { width: "10%" } },
                                "Country"
                            ),
                            React.createElement(
                                "th",
                                { style: { width: "15%" }, className: "text-right" },
                                this.props.settings.website_accessible_to_teamcaptains ? null : "Activate?"
                            )
                        )
                    ),
                    React.createElement(
                        "tbody",
                        null,
                        users.sort(sortUsersByIsActiveTeamTeamcaptain).map(function (u) {
                            return React.createElement(
                                "tr",
                                { className: u.pending ? "table-warning" : u.email !== u.old_email ? "table-info" : u.activate && !_this5.props.settings.website_accessible_to_teamcaptains ? "table-success" : "", key: "u-" + u.user_id },
                                React.createElement(
                                    "td",
                                    null,
                                    u.username
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    u.team
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement("input", { className: "form-control px-2 py-1", style: { height: "auto" }, type: "email", value: u.email, onChange: function onChange() {
                                            return _this5.updateEmail(event, u.user_id);
                                        } })
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    React.createElement(
                                        "button",
                                        { className: "btn btn-sm btn-outline-secondary font-size-3", onClick: function onClick() {
                                                return _this5.setEmail(u);
                                            } },
                                        "Save"
                                    )
                                ),
                                React.createElement(
                                    "td",
                                    null,
                                    u.country
                                ),
                                React.createElement(
                                    "td",
                                    { className: "text-right" },
                                    _this5.props.settings.website_accessible_to_teamcaptains ? u.is_teamcaptain ? React.createElement(
                                        "button",
                                        { className: "btn btn-outline-secondary", onClick: function onClick() {
                                                return _this5.activateTeamcaptain(u);
                                            } },
                                        u.is_active ? "De-activate" : "Activate"
                                    ) : null : React.createElement(
                                        "span",
                                        { className: "clickable font-size-4 mr-2", onClick: function onClick() {
                                                return _this5.activateUser(u);
                                            } },
                                        React.createElement(Toggle, { flag: u.activate })
                                    )
                                )
                            );
                        })
                    )
                )
            );
        }
    }]);

    return ActivateTeamcaptains;
}(React.Component);