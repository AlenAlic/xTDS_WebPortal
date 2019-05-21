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
        this.updateReceivedAmount = this.updateReceivedAmount.bind(this);
        this.giveRefund = this.giveRefund.bind(this);
        this.removePaymentRequirement = this.removePaymentRequirement.bind(this);
    }
    updateReceivedAmount() {
        const receivedAmounts = document.querySelectorAll('.team-received');
        let teamsDict = {};
        receivedAmounts.forEach(t => teamsDict[t.dataset.teamId] = (t.value !== "" ? t.value*100 : Number(t.dataset.placeholder)));
        fetch("/api/teams/update_received_amount", {method: "PATCH", credentials: 'same-origin', body: JSON.stringify(teamsDict)})
        .then(response => response.json())
        .then(result => {
                let newState = this.state.teams;
                newState.forEach(t => t.finances_data.prices.team = Number(result[t.team_id]));
                this.setState({teams: newState});
                receivedAmounts.forEach(i => i.value = "");
                $(function () {
                    $('[data-toggle="tooltip"]').tooltip("update")
                })
            }
        ).catch(error => {
            console.log('Error: \n', error);
        });
    }
    giveRefund(dancer, flag) {
        fetch("/api/contestants/" + dancer.contestant_id +"/give_refund/" + Number(flag), {method: "PATCH", credentials: 'same-origin'})
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
        const refundDancers = cancelledDancers.filter(filterHasRefund);

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
                    {dancersWithRefund.length > 0 ?
                        <li className="nav-item" role="presentation">
                            <a className="nav-link" href="#refunds" id="refunds-tab" role="tab" data-toggle="tab">Refunds</a>
                        </li>
                    : null}
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
                                               id="id" name="name" placeholder={currencyFormat(t.finances_data.prices.team)}
                                               data-toggle="tooltip" data-placement="top" data-team-id={t.team_id} data-placeholder={t.finances_data.prices.team}
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
                            <table className="table table-sm table-finances mt-2">
                                <thead>
                                <tr>
                                    <th className="font-size-4" colSpan="4">Cancelled dancers</th>
                                </tr>
                                <tr>
                                    <th style={{width: '20%'}}>Dancer</th>
                                    <th style={{width: '20%'}}>Team</th>
                                    <th style={{width: '20%'}} className="text-right">Potential refund</th>
                                    <th style={{width: '40%'}}/>
                                </tr>
                                </thead>
                                <tbody>
                                {noRefundDancers.sort(sortDancersAlphabetically).map( d => (
                                <tr key={'row'+`${d.contestant_id}`}>
                                    <td>{d.full_name}</td>
                                    <td>{d.contestant_info.team}</td>
                                    <td className="text-right">
                                        {currencyFormat(this.props.settings.merchandise_finalized ? d.payment_info.refund_entry_price : d.payment_info.refund_entry_price + d.merchandise_info.merchandise_price)}
                                    </td>
                                    <td className="text-right">
                                        <button className="btn btn-warning btn-sm my-1 mx-2" onClick={() => this.giveRefund(d, true)}>Give refund</button>
                                        <button className="btn btn-danger btn-sm my-1 mx-2" data-toggle="modal" data-target={'#remove-modal-'+`${d.contestant_id}`}
                                                data-keyboard="false" data-backdrop="static">Remove payment requirement</button>
                                    </td>
                                </tr>))}
                                <tr>
                                    <th className="font-size-4" colSpan="4">Refunds</th>
                                </tr>
                                <tr>
                                    <th style={{width: '20%'}}>Dancer</th>
                                    <th style={{width: '20%'}}>Refund reason(s)</th>
                                    <th style={{width: '20%'}} className="text-right">Refund</th>
                                    <th style={{width: '40%'}}/>
                                </tr>
                                {refundDancers.sort(sortDancersAlphabetically).map( d => (
                                <tr key={'row'+`${d.contestant_id}`}>
                                    <td>{d.full_name}</td>
                                    <td>{d.payment_info.refund_reasons}</td>
                                    <td className="text-right">{currencyFormat(d.payment_info.refund_price)}</td>
                                    <td className="text-right"><button className="btn btn-warning btn-sm my-1 mx-2" onClick={() => this.giveRefund(d, false)}>Remove refund</button></td>
                                </tr>))}
                                </tbody>
                            </table>
                        </div>
                    : null}
                </div>
                {noRefundDancers.sort(sortDancersAlphabetically).map( d => (
                    <div className="modal fade" id={'remove-modal-'+`${d.contestant_id}`} key={'remove-modal-'+`${d.contestant_id}`} tabIndex="-1" role="dialog" data-keyboard="false" data-backdrop="static">
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
            </React.Fragment>
        )
    }
}
