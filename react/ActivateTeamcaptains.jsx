class ActivateTeamcaptains extends React.Component {
    constructor(props) {
        super(props);
        this.state = {users: this.props.users};
    };
    setPending(u) {
        u.pending = true;
        let newState = this.state.users;
        newState[u.user_id] = u;
        this.setState({user: newState});
    };
    updateEmail(event, user_id) {
        let newState = this.state.users;
        newState[user_id].email = event.target.value;
        this.setState({user: newState});
    };
    setEmail(u) {
        if (validateEmail(u.old_email) || u.email === "") {
            this.setPending(u);
            let newState = this.state.users;
            fetch("/api/users/" + u.user_id + "/set_email", {method: "PATCH", credentials: 'same-origin', body: JSON.stringify(u)})
                .then(response => response.json())
                .then(result => {
                        newState[result.user_id] = result;
                        this.setState({user: newState})
                    }
                ).catch(error => {
                    console.log('Error: \n', error);
                    u.pending = false;
                    newState[u.user_id] = u;
                    this.setState({user: newState})
            });
        } else {
            alert("Please enter a valid e-mail address.");
        }
    };
    activateUser(u) {
        if (validateEmail(u.old_email)) {
            this.setPending(u);
            let newState = this.state.users;
            fetch("/api/users/" + u.user_id +"/activate/" + Number(!u.activate), {method: "PATCH", credentials: 'same-origin'})
            .then(response => response.json())
            .then(result => {
                    newState[result.user_id] = result;
                    this.setState({user: newState})
                }
            ).catch(error => {
                console.log('Error: \n', error);
                u.pending = false;
                newState[u.user_id] = u;
                this.setState({user: newState})
            });
        } else {
            alert("Please save a valid e-mail address, before you activate the teamcaptain.");
        }
    };
    activateTeamcaptain(u) {
        if (validateEmail(u.old_email)) {
            this.setPending(u);
            let newState = this.state.users;
            fetch("/api/users/" + u.user_id +"/activate_teamcaptain/" + Number(!u.is_active), {method: "PATCH", credentials: 'same-origin'})
            .then(response => response.json())
            .then(result => {
                    newState[result.user_id] = result;
                    this.setState({user: newState})
                }
            ).catch(error => {
                console.log('Error: \n', error);
                u.pending = false;
                newState[u.user_id] = u;
                this.setState({user: newState})
            });
        } else {
            alert("Please save a valid e-mail address, before you activate the teamcaptain.");
        }
    };

    render() {
        const users = Object.values(this.state.users);
        const teamcaptains = users.filter(filterUserIsTeamcaptain);
        const activateTeamcaptains = teamcaptains.filter(filterUserActivate);
        const activeTeamcaptains = teamcaptains.filter(filterUserIsActive);
        const treasurers = users.filter(filterUserIsTreasurer);
        const activeTreasurers = treasurers.filter(filterUserIsActive);

        return (
            <React.Fragment>
                {this.props.settings.website_accessible_to_teamcaptains ?
                    <h2>Active Teamcaptains <span className="badge badge-pill badge-dark">{activeTeamcaptains.length} / {teamcaptains.length}</span>{this.props.settings.website_accessible_to_teamcaptains ? <span> and Treasurers <span className="badge badge-pill badge-dark">{activeTreasurers.length} / {treasurers.length}</span></span> : null}</h2>
                    : <h2>Activate Teamcaptains <span className="badge badge-pill badge-dark">{activateTeamcaptains.length} / {teamcaptains.length}</span></h2>}
                <table className="table table-sm">
                    <thead>
                        <tr>
                            <th style={{width: "20%"}}>Username</th>
                            <th style={{width: "15%"}}>Team</th>
                            <th style={{width: "25%"}}>E-mail</th>
                            <th style={{width: "15%"}}/>
                            <th style={{width: "10%"}}>Country</th>
                            <th style={{width: "15%"}} className="text-right">{this.props.settings.website_accessible_to_teamcaptains ? null : "Activate?"}</th>
                        </tr>
                    </thead>
                    <tbody>
                    {users.sort(sortUsersByIsActiveTeamTeamcaptain).map(u => (
                        <tr className={u.pending ? "table-warning" : u.email !== u.old_email ? "table-info" : u.activate && !this.props.settings.website_accessible_to_teamcaptains ? "table-success": ""} key={`u-${u.user_id}`}>
                            <td>{u.username}</td>
                            <td>{u.team}</td>
                            <td><input className="form-control px-2 py-1" style={{height: "auto"}} type="email" value={u.email} onChange={() => this.updateEmail(event, u.user_id)}/></td>
                            <td><button className="btn btn-sm btn-outline-secondary font-size-3" onClick={() => this.setEmail(u)}>Save</button></td>
                            <td>{u.country}</td>
                            <td className="text-right">
                                {this.props.settings.website_accessible_to_teamcaptains ?
                                    u.is_teamcaptain ? <button className="btn btn-outline-secondary" onClick={() => this.activateTeamcaptain(u)}>{u.is_active ? "De-activate" : "Activate"}</button> : null :
                                    <span className="clickable font-size-4 mr-2" onClick={() => this.activateUser(u)}><Toggle flag={u.activate}/></span>
                                }
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </React.Fragment>
        )
    }
}