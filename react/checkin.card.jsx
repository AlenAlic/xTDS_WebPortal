import React from 'react';
import ReactDom from 'react-dom';
import CircularProgress from '@material-ui/core/CircularProgress';

const classNames = (...args) => args.join(' ');
const countCheckedIn = (obj) => {return obj.status_info.checked_in}

const Icon = ({variant="alert", className="mx-1"}) => {
    return (
        <img className={className} style={{width:"20px", height:"20px"}} src={`/static/octicons/${variant}.svg`}/>
    )
}
const Button = ({variant="primary", text, size, className, onClick, type="button"}) => {
    const classPrefix = "btn"
    const classes = classNames(className, classPrefix, `${classPrefix}-${variant}`, size && `${classPrefix}-${size}`);
    return (
        <button className={classes} onClick={onClick} type={type}>{text}</button>
    )
}

class CheckInCard extends React.Component {
    constructor(props) {
        super(props);
        this.state = { dancers: [] };
        this.checkInOnClick = this.checkInOnClick.bind(this);
        this.paymentOnClick = this.paymentOnClick.bind(this);
        this.merchandiseReceivedOnClick = this.merchandiseReceivedOnClick.bind(this);
    }
    componentDidMount() {
        this.getTeamConfirmedDancers()
    }
    getTeamConfirmedDancers() {
        fetch("/api/teams/"+this.props.team_id+"/confirmed_dancers", {method: "GET", credentials: 'same-origin'})
        .then(response => response.json())
        .then(res => {this.setState({dancers: res})} )
    }
    checkCancelledDancersMerchandise() {
        fetch("/api/teams/" + this.props.team_id +"/cancelled_dancers_with_merchandise", {method: "GET", credentials: 'same-origin'})
        .then(response => response.json())
        .then(res => {
                let myList = []
                for (var i=0; i < res.length; i++) { myList.push(res[i].full_name)}
                res.length > 0 ? alert(`Warning!\n\nThere are dancers that have ordered merchandise, but have cancelled their registration.\n\nThese are:\n${myList.join('\n')}\n\nPlease give the merchandise of those dancers to the team captain.`) : null
            }
        )
    }
    alertCheckInIncomplete(d, idx) {
        let incomplete = !d.payment_info.all_paid || !(d.merchandise_info.ordered_merchandise ? d.merchandise_info.merchandise_received ? true: false: true) || !(d.status_info.dancing_lead ? d.status_info.received_starting_number : true)
        if (incomplete) {
            if (d.status_info.checked_in) {
                fetch("/api/contestants/" + d.contestant_id +"/status_info/checked_in", {method: "PATCH", credentials: 'same-origin'})
                .then(response => response.json())
                .then(res => {
                        let dan = this.state.dancers
                        dan[idx] = res
                        this.setState({dancers: dan})
                    }
                )
            } else {
                alert("ATTENTION!\n\nCheck if the dancer has paid, received their merchandise, and has received his/her number.")
            }
        } else {
            fetch("/api/contestants/" + d.contestant_id +"/status_info/checked_in", {method: "PATCH", credentials: 'same-origin'})
            .then(response => response.json())
            .then(res => {
                    let dan = this.state.dancers
                    dan[idx] = res
                    this.setState({dancers: dan})
                    res.contestant_info.team_captain && res.status_info.checked_in ? this.checkCancelledDancersMerchandise() : null
                }
            )
        }
    }
    checkInOnClick(id, idx) {
        fetch("/api/contestants/" + id, {method: "GET", credentials: 'same-origin'})
        .then(response => response.json())
        .then(res => {
                this.alertCheckInIncomplete(res, idx)
            }
        )
    }
    paymentOnClick(id, idx) {
        fetch("/api/contestants/" + id +"/payment_info/entry_paid", {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(res => {
                let dan = this.state.dancers
                dan[idx] = res
                this.setState({dancers: dan})
            }
        )
    }
    merchandisePaymentOnClick(id, idx) {
        fetch("/api/contestants/" + id +"/payment_info/merchandise_paid", {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(res => {
                let dan = this.state.dancers
                dan[idx] = res
                this.setState({dancers: dan})
            }
        )
    }
    merchandiseReceivedOnClick(id, idx) {
        fetch("/api/contestants/" + id +"/merchandise_info/merchandise_received", {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(res => {
                let dan = this.state.dancers
                dan[idx] = res
                this.setState({dancers: dan})
            }
        )
    }
    receivedNumberOnClick(id, idx) {
        fetch("/api/contestants/" + id +"/status_info/received_starting_number", {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(res => {
                let dan = this.state.dancers
                dan[idx] = res
                this.setState({dancers: dan})
            }
        )
    }
    
    render() {
        return (
            <div className={this.state.dancers.filter(countCheckedIn).length == this.state.dancers.length && this.state.dancers.length > 0 ? "card success" : "card"} id="render-team-card-{{team['team_id']}}">
                <div className="card-header" role="button" id={'heading-'+`${this.props.team_id}`} data-toggle="collapse" href={'#collapse-'+`${this.props.team_id}`}  aria-expanded="false" aria-controls={'collapse-'+`${this.props.team_id}`} >
                    <b className="card-title">{this.props.teamName} {this.state.dancers.length == 0 ? <CircularProgress color="inherit" className="ml-3" size={19} thickness={6} /> : <span className="badge badge-pill badge-dark"> {this.state.dancers.filter(countCheckedIn).length} / {this.state.dancers.length}</span>}</b>
                </div>
                <div id={'collapse-'+`${this.props.team_id}`} className="collapse" role="tabpanel" aria-labelledby={'heading-'+`${this.props.team_id}`}>
                    {this.state.dancers.length == 0 ? null : (
                        <table className="table table-sm table-hover mb-0">
                            <colgroup>
                                <col span="1" style={{width: '15%'}}/>
                                <col span="1" style={{width: '5%'}}/>
                                <col span="1" style={{width: '15%'}}/>
                                <col span="1" style={{width: '10%'}}/>
                                <col span="1" style={{width: '15%'}}/>
                                <col span="1" style={{width: '13%'}}/>  
                                <col span="1" style={{width: '4%'}}/>
                                <col span="1" style={{width: '13%'}}/>
                                <col span="1" style={{width: '10%'}}/>
                            </colgroup>
                            <thead>
                                <tr>
                                    <th colSpan="4"></th>
                                    <th colSpan="2">Merchandise</th>
                                    <th colSpan="3">Starting number</th>
                                </tr>
                                <tr>
                                    <th>Name</th>
                                    <th>Student</th>
                                    <th>Entry fee</th>
                                    <th>Ordered</th>
                                    <th>Paid</th>
                                    <th>Received</th>
                                    <th>#</th>
                                    <th>Received</th>
                                    <th>Checked in</th>
                                </tr>
                            </thead>
                            <tbody>
                            {this.state.dancers.map((d, idx) =>
                                (   
                                    <tr className={d.status_info.checked_in && d.payment_info.all_paid && (d.status_info.dancing_lead ? d.status_info.received_starting_number : true) ? 'table-success': null} key={'tr'+`${d.contestant_id}`} >
                                        <td key={'td_name'+`${d.contestant_id}`}>
                                            {d.full_name}{d.contestant_info.team_captain ? ' - TC': null}
                                        </td>
                                        <td key={'td_student'+`${d.contestant_id}`}>
                                            {d.contestant_info.student == "student" ? "Yes": d.contestant_info.student == "non-student" ? "No" : "PhD student"}
                                        </td>
                                        <td key={'td_paid_button'+`${d.contestant_id}`}>
                                            {d.payment_info.entry_paid ? <Icon variant="check"/>: <Icon variant="x"/>}<Button size='sm' className="ml-2" onClick={() => this.paymentOnClick(d.contestant_id, idx)} key={'paid_button'+`${d.contestant_id}`} variant='outline-dark' id={d.contestant_id} text={d.payment_info.entry_paid ? 'Cancel payment': 'Confirm payment'}/>
                                        </td>
                                        <td key={'td_merchandise_ordered'+`${d.contestant_id}`}>
                                            {d.merchandise_info.ordered_merchandise ? "Yes:\u00A0": null}{"d.merchandise_info.t_shirt" == "No" ? "👕": null}{d.merchandise_info.mug ? "🍺": null}{d.merchandise_info.bag ? "👜": null}
                                        </td>
                                        <td key={'td_merchandise_payment'+`${d.contestant_id}`}>
                                            {d.merchandise_info.ordered_merchandise ? d.payment_info.merchandise_paid ? <Icon variant="check"/>: <Icon variant="x"/>: null}{d.merchandise_info.ordered_merchandise ? <Button size='sm' className="ml-2" onClick={() => this.merchandisePaymentOnClick(d.contestant_id, idx)} key={'merchandise_payment_button'+`${d.contestant_id}`} variant='outline-dark' id={d.contestant_id} text={d.payment_info.merchandise_paid ? 'Cancel payment': 'Confirm payment'}/>: null}
                                        </td>
                                        <td key={'td_merchandise_button'+`${d.contestant_id}`}>
                                            {d.merchandise_info.ordered_merchandise ? d.merchandise_info.merchandise_received ? <Icon variant="check"/>: <Icon variant="x"/>: null}{d.merchandise_info.ordered_merchandise ? <Button size='sm' className="ml-2" onClick={() => this.merchandiseReceivedOnClick(d.contestant_id, idx)} key={'merchandise_button'+`${d.contestant_id}`} variant='outline-dark' id={d.contestant_id} text={d.merchandise_info.merchandise_received ? 'Withdraw merch': 'Give merch'}/>: null}
                                        </td>
                                        <td key={'td_number'+`${d.contestant_id}`}>
                                            {d.status_info.dancing_lead ? d.contestant_info.number : null}
                                        </td>
                                        <td key={'td_number_button'+`${d.contestant_id}`}>
                                            {d.status_info.dancing_lead ? (d.status_info.received_starting_number ? <Icon variant="check"/>: <Icon variant="x"/>) : null}{d.status_info.dancing_lead ? <Button size='sm' className="ml-2" onClick={() => this.receivedNumberOnClick(d.contestant_id, idx)} key={'number_button'+`${d.contestant_id}`} variant='outline-dark' id={d.contestant_id} text={d.status_info.received_starting_number ? 'Take number': 'Give number'}/> : null }
                                        </td>
                                        <td key={'td_check_in_button'+`${d.contestant_id}`}>
                                            {d.status_info.checked_in ? <Icon variant="check"/>: <Icon variant="x"/>}<Button size='sm' className="ml-2" onClick={() => this.checkInOnClick(d.contestant_id, idx)} key={'check_in_button'+`${d.contestant_id}`} variant='outline-dark' id={d.contestant_id} text={d.status_info.checked_in ? 'Check out': 'Check in'}/>
                                        </td>
                                    </tr>
                                )
                            )}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        );
    }
}


class CheckInTables extends React.Component {
    constructor(props) {
        super(props);
        this.state = { ids: [] };
    }
    componentDidMount() {
        fetch("/check_in_assistant/check_in_teams", {method: "GET", credentials: 'same-origin'})
        .then(response => response.json())
        .then(res => {
            this.setState({ids: res})
        })
    }
    render() {
        return (
            <React.Fragment>
                {this.state.ids.map(team =>  <CheckInCard key={team.name} team_id={team.team_id} teamName={team.name} />)}
            </React.Fragment>
        )
    }
}

ReactDom.render(
    <CheckInTables />,
    document.getElementById("accordion")
);