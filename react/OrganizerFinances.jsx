const OrganizerFinancesDropDown = ({teams, text}) => {
    return (
        <li className="nav-item dropdown">
            <a className="nav-link dropdown-toggle" data-toggle="dropdown" data-display="static" href="#" role="button">{text} teams</a>
            <div className="dropdown-menu">
                {teams.sort(sortTeamsAlphabetically).map( t => (
                    <a className="dropdown-item" id={`team-${t.team_id}`} href={`#tab-${t.team_id}`} key={`team-${t.team_id}`} data-toggle="tab" role="tab">
                        {t.name} <span className="badge badge-pill badge-dark">{Object.values(t.finances_data.dancers).filter(filterAllPaid).length} / {Object.values(t.finances_data.dancers).length}</span>
                    </a>
                ))}
            </div>
        </li>
    );
};


class OrganizerFinances extends React.Component {
    constructor(props) {
        super(props);
        this.state = {teams: this.props.teams};
    }
    updateReceivedAmount() {
        const receivedAmounts = document.querySelectorAll('.team-received');
        let teamsDict = {};
        receivedAmounts.forEach(t => teamsDict[t.dataset.teamId] = (t.value !== "" ? t.value*100 : Number(t.dataset.placeholder)));
        fetch("/api/teams/update_received_amount", {method: "PATCH", credentials: 'same-origin', body: JSON.stringify(teamsDict)})
        .then(response => response.json())
        .then(result => {
                let newState = this.state.teams;
                Object.values(newState).forEach(t => t.finances_data.prices.team = Number(result[t.team_id]));
                this.setState({teams: newState});
                receivedAmounts.forEach(i => i.value = "");
                $(function () {
                    $('[data-toggle="tooltip"]').tooltip("dispose").tooltip()
                })
            }
        ).catch(error => {
            console.log('Error: \n', error);
        });
    }
    giveEntryFeeRefund(dancer) {
        fetch("/api/contestants/" + dancer.contestant_id +"/give_entry_fee_refund", {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(result => {
                let newState = this.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                this.setState({teams: newState})
            }
        ).catch(error => {
            console.log('Error: \n', error);
        });
    }
    removePaymentRequirement(dancer, flag) {
        fetch("/api/contestants/" + dancer.contestant_id +"/remove_payment_requirement/", {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(result => {
                let newState = this.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                this.setState({teams: newState})
            }
        ).catch(error => {
            console.log('Error: \n', error);
        });
    }
    giveGeneralRefund() {
        let dancer = document.getElementById("general-dancer");
        let contestant_id = dancer.options[dancer.selectedIndex].value;
        let name = dancer.options[dancer.selectedIndex].innerText;
        let data = {
            "reason": document.getElementById("general-reason").value,
            "amount": document.getElementById("general-amount").value
        };
        dancer.selectedIndex = 0;
        document.getElementById("general-reason").value = "";
        document.getElementById("general-amount").value = "";
        fetch("/api/contestants/" + contestant_id +"/give_general_refund", {method: "PATCH", credentials: 'same-origin', body: JSON.stringify(data)})
        .then(response => response.json())
        .then(result => {
                let newState = this.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                this.setState({teams: newState});
                $.notify({message: `Refund given to ${name}.`},{type: 'alert-info'});
            }
        ).catch(error => {
            console.log('Error: \n', error);
        });
    }
    updateRefund(dancer, refund) {
        let data = {
            "reason": document.getElementById("reason-"+refund.refund_id).value,
            "amount": document.getElementById("amount-"+refund.refund_id).value
        };
        fetch("/api/contestants/" + dancer.contestant_id + "/update_refund/" + refund.refund_id, {method: "PATCH", credentials: 'same-origin', body: JSON.stringify(data)})
        .then(response => response.json())
        .then(result => {
                let newState = this.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                this.setState({teams: newState})
            }
        ).catch(error => {
            console.log('Error: \n', error);
        });
    }
    deleteRefund(dancer, refund) {
        fetch("/api/contestants/" + dancer.contestant_id + "/delete_refund/" + refund.refund_id, {method: "PATCH", credentials: 'same-origin'})
        .then(response => response.json())
        .then(result => {
                let newState = this.state.teams;
                newState[result.contestant_info.team_id].finances_data.dancers[result.contestant_id] = result;
                this.setState({teams: newState})
            }
        ).catch(error => {
            console.log('Error: \n', error);
        });
    }

    render() {
        const teams = Object.values(this.state.teams);
        const activeTeams = teams.filter(filterTeamsWithDancers);
        const DutchTeams = activeTeams.filter(filterDutchTeams);
        const GermanTeams = activeTeams.filter(filterGermanTeams);
        const OtherTeams = activeTeams.filter(filterOtherTeams);

        const dancers = [].concat.apply([], teams.map(team => Object.values(team.finances_data.dancers)));
        const students = dancers.filter(filterStudents);
        const phdStudents = dancers.filter(filterPhDStudents);
        const nonStudents = dancers.filter(filterNonStudents);
        const dancersWithMerchandise = dancers.filter(filterHasMerchandise);
        const merchandise = dancersWithMerchandise.map(dancer => Object.values(dancer.merchandise_info.purchases).length).reduce(reduceArraySum, 0);

        const dancersOwedPrice = dancers.map(mapPaymentPrice).reduce(reduceArraySum, 0);
        const teamsReceivedPrice = activeTeams.map(team => team.finances_data.prices.team).reduce(reduceArraySum, 0);
        const differencePrice = teamsReceivedPrice - dancersOwedPrice;
        const dancersWithRefund = dancers.filter(filterHasRefund);
        const refundPrice = dancersWithRefund.map(mapRefundPrice).reduce(reduceArraySum, 0);

        const cancelledDancers = dancers.filter(filterCancelled);
        const noRefundDancers = cancelledDancers.filter(filterDoesNotHaveRefund).filter(filterPaymentRequired);
        const refundDancers = dancers.filter(filterHasRefund);

        return (
            <React.Fragment>
                <h2>Financial overview</h2>
                <p>Don't forget to save any changes made here.</p>
                <ul className="nav nav-tabs" id="myTabs" role="tablist">
                    <li className="nav-item" role="presentation">
                        <a className="nav-link active" href="#all-teams" id="all-teams-tab" role="tab" data-toggle="tab">All teams</a>
                    </li>
                    {DutchTeams.length > 0 ? <OrganizerFinancesDropDown text={"Dutch"} teams={DutchTeams}/> : null}
                    {GermanTeams.length > 0 ? <OrganizerFinancesDropDown text={"German"} teams={GermanTeams}/> : null}
                    {OtherTeams.length > 0 ? <OrganizerFinancesDropDown text={"Other"} teams={OtherTeams}/> : null}
                    <li className="nav-item" role="presentation">
                        <a className={dancersWithRefund.length > 0 ? "nav-link" : "nav-link disabled"} href="#refunds" id="refunds-tab" role="tab" data-toggle="tab">Refunds</a>
                    </li>
                </ul>
                <div className="tab-content">
                    <div className="tab-pane fade show active" id="all-teams">
                        <form method="POST" encType="multipart/form-data" noValidate>
                            <input className="btn btn-outline-primary float-right my-2" id="submit-download_file" name="download_file" type="submit" value="Download overview"/>
                        </form>
                        <button className="btn btn-outline-primary my-2" type="button" onClick={() => this.updateReceivedAmount()}>Save changes</button>
                        <table className="table table-sm">
                            <thead>
                            <tr className="finances-summary-row">
                                {this.props.settings.phd_student_category ?
                                    <React.Fragment>
                                        <th style={{width: '18%'}}>Team</th>
                                        <th style={{width: '10%'}}>Students</th>
                                        <th style={{width: '10%'}}>PhD students</th>
                                    </React.Fragment>
                                    :
                                    <React.Fragment>
                                        <th style={{width: '28%'}}>Team</th>
                                        <th style={{width: '10%'}}>Students</th>
                                    </React.Fragment>}
                                <th style={{width: '10%'}}>Non students</th>
                                <th style={{width: '10%'}}>{this.props.settings.merchandise ? "Merchandise" : null}</th>
                                <th style={{width: '13%'}}>Owed</th>
                                <th style={{width: '9%'}}>Received</th>
                                <th style={{width: '8%'}}>Difference</th>
                                <th style={{width: '12%'}}>Refund</th>
                            </tr>
                            </thead>
                            <tbody>
                            {activeTeams.sort(sortTeamsAlphabetically).map( t => {
                                const dancers = Object.values(t.finances_data.dancers);
                                const students = dancers.filter(filterStudents);
                                const phdStudents = dancers.filter(filterPhDStudents);
                                const nonStudents = dancers.filter(filterNonStudents);
                                const dancersWithMerchandise = dancers.filter(filterHasMerchandise);
                                const merchandise = dancersWithMerchandise.map(dancer => Object.values(dancer.merchandise_info.purchases).length).reduce(reduceArraySum, 0);

                                const dancersOwedPrice = dancers.map(mapPaymentPrice).reduce(reduceArraySum, 0);
                                const differencePrice = t.finances_data.prices.team - dancersOwedPrice;
                                const refundPrice = dancers.filter(filterHasRefund).map(mapRefundPrice).reduce(reduceArraySum, 0);

                                return (
                                <tr className={`finances-summary-row ${differencePrice === 0 ? "table-success" : differencePrice > 0 ? "table-warning" : "table-danger"}`} key={`team-total-${t.team_id}`}>
                                    <td>{t.name}</td>
                                    <td>{students.length}</td>
                                    {this.props.settings.phd_student_category ?
                                        <td>{phdStudents.length}</td>
                                        : null}
                                    <td>{nonStudents.length}</td>
                                    <td>{this.props.settings.merchandise ? merchandise : null}</td>
                                    <td>{currencyFormat(dancersOwedPrice)}</td>
                                    <td>
                                        <input className="form-control text-right px-0 py-0 team-received"
                                               style={{height: "auto"}} type="number" min="0" step="0.01"
                                               placeholder={currencyFormat(t.finances_data.prices.team)}
                                               data-toggle="tooltip" data-placement="top"
                                               data-team-id={t.team_id} data-placeholder={t.finances_data.prices.team}
                                               title={currencyFormat(t.finances_data.prices.team)}/>
                                    </td>
                                    <td>{currencyFormat(differencePrice)}</td>
                                    <td>{currencyFormat(refundPrice)}</td>
                                </tr>
                            )})}
                            <tr className="finances-summary-row">
                                <th/>
                                <th>{students.length}</th>
                                {this.props.settings.phd_student_category ?
                                    <th>{phdStudents.length}</th>
                                    : null}
                                <th>{nonStudents.length}</th>
                                <th>{this.props.settings.merchandise ? merchandise : null}</th>
                                <th>{currencyFormat(dancersOwedPrice)}</th>
                                <th>{currencyFormat(teamsReceivedPrice)}</th>
                                <th>{currencyFormat(differencePrice)}</th>
                                <th>{currencyFormat(refundPrice)}</th>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                    {activeTeams.sort(sortTeamsAlphabetically).map( t => (
                        <div className="tab-pane fade" id={`tab-${t.team_id}`} key={`tab-${t.team_id}`} role="tabpanel">
                            <TeamCaptainFinances dancers={t.finances_data.dancers} settings={t.finances_data.settings} prices={t.finances_data.prices} merchandise_items={t.finances_data.merchandise_items}/>
                        </div>
                    ))}
                    {cancelledDancers.length > 0 ?
                        <div className="tab-pane fade" id="refunds">
                            {noRefundDancers.length > 0 ?
                                <table className="table table-sm mt-2">
                                    <tbody>
                                        <tr>
                                            <th className="font-size-4" colSpan="5">Cancelled dancers</th>
                                        </tr>
                                        <tr>
                                            <th style={{width: '20%'}}>Dancer</th>
                                            <th style={{width: '40%'}}>Team</th>
                                            <th style={{width: '20%'}} className="text-right">Potential refund</th>
                                            <th style={{width: '20%'}}/>
                                        </tr>

                                    {noRefundDancers.sort(sortDancersAlphabetically).map( d => (
                                    <tr key={'row'+`${d.contestant_id}`}>
                                        <td>{d.full_name}</td>
                                        <td>{d.contestant_info.team}</td>
                                        <td className="text-right">{currencyFormat(d.payment_info.entry_price_refund)}</td>
                                        <td className="text-right">
                                            <button className="btn btn-danger btn-sm d-inline-block my-1" data-toggle="modal" data-target={'#remove-modal-'+`${d.contestant_id}`}
                                                    data-keyboard="false" data-backdrop="static">Remove payment requirement</button>
                                            <button className="btn btn-warning btn-sm d-inline-block my-1" onClick={() => this.giveEntryFeeRefund(d)}>Give entry fee refund</button>
                                        </td>
                                    </tr>))}
                                    </tbody>
                                </table>
                                : null}
                            <div className="card mt-2">
                                <div className="card-body">
                                    <h5 className="card-title">Give refund</h5>
                                    <form className="form" method="POST" encType="multipart/form-data" noValidate>
                                        <div className="form-group">
                                            <label htmlFor="general-dancer">Dancer</label>
                                            <select className="form-control" id="general-dancer">
                                                <option value={0}>Select dancer</option>
                                                {dancers.sort(sortDancersAlphabetically).map(d => (
                                                    <option key={'option-'+`${d.contestant_id}`} value={d.contestant_id}>{d.full_name}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label htmlFor="general-reason">Refund reason</label>
                                            <input type="text" className="form-control" id="general-reason"/>
                                        </div>
                                        <div className="form-group">
                                            <label htmlFor="general-amount">Refund amount (eurocents)</label>
                                            <input type="number" className="form-control" id="general-amount" min="0" step="1"/>
                                        </div>
                                        <button type="button" className="btn btn-primary" onClick={() => this.giveGeneralRefund()}>Give refund</button>
                                    </form>
                                </div>
                            </div>
                            <table className="table table-sm mt-2">
                                <tbody>
                                <tr>
                                    <th className="font-size-4" colSpan="4">Refunds</th>
                                </tr>
                                <tr>
                                    <th style={{width: '20%'}}>Dancer</th>
                                    <th style={{width: '40%'}}>Refund</th>
                                    <th style={{width: '20%'}} className="text-right">Amount</th>
                                    <th style={{width: '20%'}} className="text-right"/>
                                </tr>
                                {refundDancers.sort(sortDancersAlphabetically).map( d => (
                                    <React.Fragment key={'row-'+`-${d.contestant_id}`}>
                                        {d.payment_info.refunds.map((r, i) => (
                                            (i === 0 ?
                                                <tr key={'row-'+r.refund_id+`-${d.contestant_id}`}>
                                                    <td>{d.full_name}</td>
                                                    <td>{r.reason}</td>
                                                    <td className="text-right ">{currencyFormat(r.amount)}</td>
                                                    <td className="text-right">
                                                        <button className="btn btn-info btn-sm" data-toggle="modal" data-target={'#update-modal-'+r.refund_id}
                                                                data-keyboard="false" data-backdrop="static">Edit</button>
                                                        <button className="btn btn-danger btn-sm ml-1" data-toggle="modal" data-target={'#delete-modal-'+r.refund_id}
                                                                data-keyboard="false" data-backdrop="static">Delete</button>
                                                    </td>
                                                </tr> :
                                                <tr key={'row-'+r.refund_id+`-${d.contestant_id}`}>
                                                    <td className="border-0"/>
                                                    <td className="border-0">{r.reason}</td>
                                                    <td className="border-0 text-right">{currencyFormat(r.amount)}</td>
                                                    <td className="border-0 text-right">
                                                        <button className="btn btn-info btn-sm" data-toggle="modal" data-target={'#update-modal-'+r.refund_id}
                                                                data-keyboard="false" data-backdrop="static">Edit</button>
                                                        <button className="btn btn-danger btn-sm ml-1" data-toggle="modal" data-target={'#delete-modal-'+r.refund_id}
                                                                data-keyboard="false" data-backdrop="static">Delete</button>
                                                    </td>
                                                </tr>)
                                        ))}
                                        <tr>
                                            <td className="border-0"/>
                                            <td className="border-0 text-right"><b>Total</b></td>
                                            <td className="border-0 text-right"><b>{currencyFormat(d.payment_info.refund_price)}</b></td>
                                            <td className="border-0 text-right"/>
                                        </tr>
                                    </React.Fragment>
                                ))}
                                </tbody>
                            </table>
                        </div>
                    : null}
                </div>
                {noRefundDancers.map( d => (
                    <div className="modal fade" id={'remove-modal-'+`${d.contestant_id}`} key={'remove-add-modal-'+`${d.contestant_id}`} tabIndex="-1" role="dialog" data-keyboard="false" data-backdrop="static">
                        <div className="modal-dialog modal-lg" role="document">
                            <div className="modal-content">
                                <div className="modal-header">
                                    <h5 className="modal-title">Remove payment requirement</h5>
                                    <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                                        <span aria-hidden="true">&times;</span>
                                    </button>
                                </div>
                                <div className="modal-body">
                                    <p>You are about to remove the payment requirement of {d.full_name}.</p>
                                    <p>Are you sure you wish to do this?</p>
                                </div>
                                <div className="modal-footer">
                                    <button type="button" className="btn btn-secondary" data-dismiss="modal">No</button>
                                    <button type="button" className="btn btn-primary" data-dismiss="modal" onClick={() => this.removePaymentRequirement(d)}>Yes</button>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
                {refundDancers.map( d => (
                    d.payment_info.refunds.map(r => (
                        <React.Fragment  key={'modals-'+r.refund_id}>
                            <div className="modal fade" id={'update-modal-'+r.refund_id} tabIndex="-1" role="dialog" data-keyboard="false" data-backdrop="static">
                                <div className="modal-dialog modal-lg" role="document">
                                    <div className="modal-content">
                                        <div className="modal-header">
                                            <h5 className="modal-title">Edit refund</h5>
                                            <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                                                <span aria-hidden="true">&times;</span>
                                            </button>
                                        </div>
                                        <div className="modal-body">
                                            <div className="form-group">
                                                <label htmlFor={'reason-'+r.refund_id}>Refund reason</label>
                                                <input type="text" className="form-control" id={'reason-'+r.refund_id} defaultValue={r.reason}/>
                                            </div>
                                            <div className="form-group">
                                                <label htmlFor={'amount-'+r.refund_id}>Refund amount (eurocents)</label>
                                                <input type="text" className="form-control" id={'amount-'+r.refund_id} defaultValue={r.amount}/>
                                            </div>
                                        </div>
                                        <div className="modal-footer">
                                            <button type="button" className="btn btn-secondary" data-dismiss="modal">Cancel</button>
                                            <button type="button" className="btn btn-primary" data-dismiss="modal" onClick={() => this.updateRefund(d, r)}>Save</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="modal fade" id={'delete-modal-'+r.refund_id} tabIndex="-1" role="dialog" data-keyboard="false" data-backdrop="static">
                                <div className="modal-dialog modal-lg" role="document">
                                    <div className="modal-content">
                                        <div className="modal-header">
                                            <h5 className="modal-title">Delete refund</h5>
                                            <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                                                <span aria-hidden="true">&times;</span>
                                            </button>
                                        </div>
                                        <div className="modal-body">
                                            <p>You are about to remove the refund of {d.full_name} for {r.reason} ({currencyFormat(r.amount)}).</p>
                                            <p>Are you sure you wish to do this?</p>
                                        </div>
                                        <div className="modal-footer">
                                            <button type="button" className="btn btn-secondary" data-dismiss="modal">No</button>
                                            <button type="button" className="btn btn-primary" data-dismiss="modal" onClick={() => this.deleteRefund(d, r)}>Yes</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </React.Fragment>
                        ))
                ))}
            </React.Fragment>
        )
    }
}