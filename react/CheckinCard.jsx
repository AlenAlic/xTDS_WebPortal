class CheckinCard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {dancers: {}};
        this.setPending = this.setPending.bind(this);
        this.entryPayment = this.entryPayment.bind(this);
        this.merchandisePayment = this.merchandisePayment.bind(this);
        this.merchandiseReceived = this.merchandiseReceived.bind(this);
        this.tryCheckIn = this.tryCheckIn.bind(this);
        this.checkIn = this.checkIn.bind(this);
    }
    componentDidMount() {
        this.getTeamDancers()
    }
    getTeamDancers() {
        fetch("/api/teams/"+this.props.team_id+"/check_in_dancers", {method: "GET", credentials: 'same-origin'})
        .then(response => response.json())
        .then(result => {this.setState({dancers: result})} )
    }
    setPending(dancer) {
        let newState = this.state.dancers;
        dancer.pending = true;
        newState[dancer.contestant_id] = dancer;
        this.setState({dancers: newState});
    };
    entryPayment(dancer) {
        this.setPending(dancer);
        let newState = this.state.dancers;
        fetch("/api/contestants/" + dancer.contestant_id +"/entry_payment/" + Number(!dancer.payment_info.entry_paid), {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(result => {
                newState[result.contestant_id] = result;
                this.setState({dancers: newState})
            }
        ).catch(error => {
            console.log('Error: \n', error);
            dancer.pending = false;
            newState[dancer.contestant_id] = dancer;
            this.setState({dancers: newState})
        });
    }
    merchandisePayment(dancer, purchase) {
        this.setPending(dancer);
        let newState = this.state.dancers;
        fetch("/api/contestants/" + dancer.contestant_id +"/merchandise_payment/" + purchase.merchandise_purchased_id + "/" + Number(!purchase.paid), {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(result => {
                newState[result.contestant_id] = result;
                this.setState({dancers: newState})
            }
        ).catch(error => {
            console.log('Error: \n', error);
            dancer.pending = false;
            newState[dancer.contestant_id] = dancer;
            this.setState({dancers: newState})
        });
    }
    merchandiseReceived(dancer, purchase) {
        this.setPending(dancer);
        let newState = this.state.dancers;
        fetch("/api/contestants/" + dancer.contestant_id +"/merchandise_received/" + purchase.merchandise_purchased_id + "/" + Number(!purchase.received), {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(result => {
                newState[result.contestant_id] = result;
                this.setState({dancers: newState})
            }
        ).catch(error => {
            console.log('Error: \n', error);
            dancer.pending = false;
            newState[dancer.contestant_id] = dancer;
            this.setState({dancers: newState})
        });
    }
    tryCheckIn(dancer) {
        if (dancer.status_info.checked_in) {
            this.checkIn(dancer)
        } else {
            let complete = dancer.payment_info.all_paid && dancer.merchandise_info.merchandise_received;
            console.log(complete);
            if (complete) {
                if (dancer.contestant_info.team_captain) {
                    this.checkCancelledDancersMerchandise()
                }
                this.checkIn(dancer)
            } else {
                if (dancer.merchandise_info.ordered_merchandise) {
                    alert("ATTENTION!\n\nCannot check in dancer.\n\nPlease check that the dancer has paid the entry fee, and has received and paid their merchandise.")
                } else {
                    alert("ATTENTION!\n\nCannot check in dancer.\n\nPlease check that the dancer has paid the entry fee.")
                }
            }
        }

    }
    checkIn(dancer) {
        this.setPending(dancer);
        let newState = this.state.dancers;
        fetch("/api/contestants/" + dancer.contestant_id +"/check_in/" + Number(!dancer.status_info.checked_in), {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(result => {
                newState[result.contestant_id] = result;
                this.setState({dancers: newState})
            }
        ).catch(error => {
            console.log('Error: \n', error);
            dancer.pending = false;
            newState[dancer.contestant_id] = dancer;
            this.setState({dancers: newState})
        });
    }
    checkCancelledDancersMerchandise() {
        fetch("/api/teams/" + this.props.team_id +"/cancelled_dancers_with_merchandise", {method: "GET", credentials: 'same-origin'})
        .then(response => response.json())
        .then(res => {
                let myList = [];
                for (let i=0; i < res.length; i++) { myList.push(res[i].full_name)}
                res.length > 0 ? alert(`ATTENTION!!\n\nThere are dancers that have ordered merchandise, but have cancelled their registration.\n\nThese are:\n${myList.join('\n')}\n\nPlease give the merchandise of those dancers to the team captain, and mark the merchandise as received in this list`) : null
            }
        )
    }
    
    render() {
        const dancers = Object.values(this.state.dancers);

        return (
            <div className={dancers.length > 0 ? dancers.filter(countCheckedIn).length === dancers.length ? "card success" : "card" : "card"}>
                <div className="card-header" role="button" id={'heading-'+`${this.props.team_id}`} data-toggle="collapse" href={'#collapse-'+`${this.props.team_id}`}  aria-expanded="false" aria-controls={'collapse-'+`${this.props.team_id}`} >
                    <b className="card-title">{this.props.team_name} {dancers.length === 0 ? <div className="spinner-border spinner-border-sm" role="status"/> : <span className="badge badge-pill badge-dark"> {dancers.filter(countSpecialCheckedIn).length} / {dancers.length}</span>}</b>
                </div>
                <div id={'collapse-'+`${this.props.team_id}`} className="collapse">
                    {dancers.length === 0 ? null : (
                        <table className="table table-hover mb-0">
                            <thead>
                                <tr>
                                    <th/>
                                    <th colSpan="3">Entry fee</th>
                                    <th colSpan="3">Merchandise</th>
                                    <th/>
                                </tr>
                                <tr>
                                    <th style={{width: '15%'}}>Name</th>
                                    <th style={{width: '10%'}}>Student</th>
                                    <th style={{width: '10%'}}>Fee</th>
                                    <th style={{width: '10%'}}>Paid</th>
                                    <th style={{width: '15%'}}>Ordered</th>
                                    <th style={{width: '15%'}}>Paid</th>
                                    <th style={{width: '15%'}}>Received</th>
                                    <th style={{width: '10%'}}>Checked in</th>
                                </tr>
                            </thead>
                            <tbody>
                            {dancers.sort(sortDancersAlphabetically).map(d =>
                                (   
                                    <tr className={d.pending ? 'table-warning': d.payment_info.all_paid && d.merchandise_info.merchandise_received ? d.status_info.checked_in && d.status_info.status === "confirmed" || d.status_info.status === "cancelled" ? 'table-success' : null: null} key={'row'+`${d.contestant_id}`} >
                                        <td>{d.full_name}{d.contestant_info.team_captain ? ' - TC': null}</td>
                                        <td>{d.contestant_info.student === "student" ? "Yes": d.contestant_info.student === "non-student" ? "No" : "PhD student"}</td>
                                        <td>{currencyFormat(this.props.prices[d.contestant_info.student])}</td>
                                        <td><button className={`btn ${d.payment_info.entry_paid ? "btn-outline-secondary" : "btn-danger"}`} onClick={() => this.entryPayment(d)}>{d.payment_info.entry_paid ? <i className="fas fa-check"/>: <i className="fas fa-times"/>}</button></td>
                                        <td>
                                            {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(p => (
                                                !p.cancelled && d.status_info.status === "confirmed" || d.status_info.status === "cancelled" ? <div key={'item'+`${p.merchandise_purchased_id}`}>{p.item} ({currencyFormat(p.price)})</div> : null
                                            )) : '-'}
                                        </td>
                                        <td>
                                            {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(p => (
                                                 !p.cancelled && d.status_info.status === "confirmed" || d.status_info.status === "cancelled" ? <div key={'paid'+`${p.merchandise_purchased_id}`}>
                                                    <button className={`btn ${p.paid ? "btn-outline-secondary" : "btn-danger"}`} onClick={() => this.merchandisePayment(d, p)}>{p.paid ? <i className="fas fa-check"/>: <i className="fas fa-times"/>} Paid</button>
                                                </div> : null
                                            )) : "-"}
                                        </td>
                                        <td>
                                            {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(p => (
                                                 !p.cancelled && d.status_info.status === "confirmed" ||  d.status_info.status === "cancelled" ? <div key={'received'+`${p.merchandise_purchased_id}`}>
                                                    <button className={`btn ${p.received ? "btn-outline-secondary" : "btn-danger"}`} onClick={() => this.merchandiseReceived(d, p)}>{p.received ? <i className="fas fa-check"/>: <i className="fas fa-times"/>} Received</button>
                                                </div> : null
                                            )) : "-"}
                                        </td>
                                        <td>{d.status_info.status === "confirmed" ? <button className={`btn ${d.status_info.checked_in ? "btn-outline-secondary" : "btn-danger"}`} onClick={() => this.tryCheckIn(d)}>{d.status_info.checked_in ? <i className="fas fa-check"/>: <i className="fas fa-times"/>}</button> : null}</td>
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