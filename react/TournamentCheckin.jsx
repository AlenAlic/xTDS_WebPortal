class TournamentCheckin extends React.Component {
    constructor(props) {
        super(props);
        this.state = {dancers: this.props.dancers};
    }
    render() {
        const dancers = Object.values(this.state.dancers);
        const confirmedDancers = dancers.filter(filterConfirmed);
        const checkedInDancers = confirmedDancers.filter(filterCheckedIn);
        const confirmedLeads = confirmedDancers.filter(filterLeads);
        const receivedStartingNumber = confirmedLeads.filter(filterStartingNumbers);
        const cancelledDancers = dancers.filter(filterCancelled);
        const cancelledDancersReceivedMerchandise = cancelledDancers.filter(filterReceivedMerchandise);

        return (
            <React.Fragment>
                <b className="d-block my-2 mt-3">Checked in <span className="badge badge-pill badge-dark">{checkedInDancers.length} / {confirmedDancers.length}</span></b>
                <b className="d-block my-2">Received starting number <span className="badge badge-pill badge-dark">{receivedStartingNumber.length} / {confirmedLeads.length}</span></b>
                <table className="table table-sm mb-5">
                    <thead>
                    <tr>
                        <th colSpan="2"/>
                        <th colSpan="3">Merchandise</th>
                        <th colSpan="2"/>
                    </tr>
                    <tr>
                        <th style={{width: '25%'}}>Dancer</th>
                        <th style={{width: '10%'}}>Paid entry fee</th>
                        <th style={{width: '25%'}}>Ordered</th>
                        <th style={{width: '10%'}}>Paid</th>
                        <th style={{width: '10%'}}>Received</th>
                        <th style={{width: '10%'}}>Checked in</th>
                        <th style={{width: '10%'}}>Got number</th>
                    </tr>
                    </thead>
                    <tbody>
                    {confirmedDancers.sort(sortDancersAlphabetically).map(d =>
                        (
                            <tr className={d.payment_info.all_paid && d.merchandise_info.merchandise_received && d.status_info.checked_in ? d.status_info.received_starting_number ? 'table-success' : 'table-primary' : null} key={'row'+`${d.contestant_id}`} >
                                <td>{d.full_name}</td>
                                <td><CheckMark flag={d.payment_info.entry_paid}/></td>
                                <td>{d.merchandise_info.merchandise_ordered ? <CheckMark flag={d.merchandise_info.merchandise_ordered}/>: null}</td>
                                <td>{d.merchandise_info.merchandise_ordered ? <CheckMark flag={d.merchandise_info.merchandise_paid}/>: null}</td>
                                <td>{d.merchandise_info.merchandise_ordered ? <CheckMark flag={d.merchandise_info.merchandise_received}/>: null}</td>
                                <td><CheckMark flag={d.status_info.checked_in}/></td>
                                <td><CheckMark flag={d.status_info.received_starting_number}/></td>
                            </tr>
                        )
                    )}
                    {cancelledDancers.length > 0 ?
                        <React.Fragment>
                            <tr>
                                <th colSpan="7" className="pt-5">Cancelled dancers with ordered merchandise <span className="badge badge-pill badge-dark">{cancelledDancersReceivedMerchandise.length} / {cancelledDancers.length}</span></th>
                            </tr>
                            <tr>
                                <th colSpan="2"/>
                                <th colSpan="3">Merchandise</th>
                                <th colSpan="2"/>
                            </tr>
                            <tr>
                                <th>Dancer</th>
                                <th>Paid entry fee</th>
                                <th>Ordered</th>
                                <th>Paid</th>
                                <th>Received</th>
                                <th colSpan="2"/>
                            </tr>
                            {cancelledDancers.sort(sortDancersAlphabetically).map(d =>
                                (
                                    <tr className={d.payment_info.all_paid && d.merchandise_info.merchandise_received ? 'table-success' : null} key={'row'+`${d.contestant_id}`} >
                                        <td>{d.full_name}</td>
                                        <td><CheckMark flag={d.payment_info.entry_paid}/></td>
                                        <td>
                                            {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(p => (
                                                <div key={'item'+`${p.merchandise_purchased_id}`}>{p.item}</div>
                                            )) : "-"}
                                        </td>
                                        <td>
                                            {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(p => (
                                                <div key={'price'+`${p.merchandise_purchased_id}`}><CheckMark flag={p.paid}/></div>
                                            )) : "-"}
                                        </td>
                                        <td>
                                            {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(p => (
                                                <div key={'paid'+`${p.merchandise_purchased_id}`}><CheckMark flag={p.received}/></div>
                                            )) : "-"}
                                        </td>
                                        <td/>
                                        <td/>
                                    </tr>
                                )
                            )}
                        </React.Fragment>
                    : null}
                    </tbody>
                </table>
            </React.Fragment>
        )
    }
}