class OrderedMerchandise extends React.Component {
    constructor(props) {
        super(props);
        this.state = {dancers: this.props.dancers};
    }
    setPending(dancer) {
        let newState = this.state.dancers;
        dancer.pending = true;
        newState[dancer.contestant_id] = dancer;
        this.setState({dancers: newState});
    };
    itemOrdered(dancer, purchase) {
        this.setPending(dancer);
        let newState = this.state.dancers;
        fetch("/api/contestants/" + dancer.contestant_id +"/purchase_ordered/" + purchase.merchandise_purchased_id + "/" + Number(!purchase.ordered), {method: "PATCH", credentials: 'same-origin'})
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
    render() {
        const dancers = Object.values(this.state.dancers).sort(sortDancersAlphabetically);

        return (
            <div className="panel-group page-break" id="merchandise-dancers">
                <div className="card">
                    <div className="card-header clickable" role="button" id="headingOne" data-toggle="collapse"
                         data-parent="#merchandise-dancers" href="#collapseOne">Dancers that have purchased merchandise <span className="badge badge-pill badge-dark">{dancers.length}</span>
                    </div>
                    <div id="collapseOne" className="collapse show card-body px-0 py-0">
                        {dancers.length > 0 ?
                            <table className="table table-sm mb-0">
                                <thead>
                                <tr>
                                    <th style={{width: '20%'}}>Dancer</th>
                                    <th style={{width: '20%'}}>Email</th>
                                    <th style={{width: '20%'}}>Team</th>
                                    <th style={{width: '20%'}}>Item</th>
                                    <th style={{width: '8%'}}>Ordered</th>
                                    <th style={{width: '5%'}}>Paid</th>
                                    <th style={{width: '7%'}}>Received</th>
                                </tr>
                                </thead>
                                <tbody>
                                {dancers.map(d => (
                                    Object.values(d.merchandise_info.purchases).map((p, i) => (
                                    <tr className={d.pending ? "table-warning" : p.ordered && p.paid && p.received ? "table-success" : null} key={`row-${d.contestant_id}`}>
                                        {i === 0 ?
                                        <React.Fragment>
                                            <td>{d.full_name}</td>
                                            <td>{d.email}</td>
                                            <td>{d.contestant_info.team}</td>
                                        </React.Fragment>
                                        : <td colSpan="3"/>}
                                        <td>{p.item}</td>
                                        <td><input type="checkbox" onChange={() => this.itemOrdered(d,p)} checked={p.ordered}/></td>
                                        <td><CheckMark flag={p.paid}/></td>
                                        <td><CheckMark flag={p.received}/></td>
                                    </tr>
                                    ))
                                ))}
                                </tbody>
                            </table>
                            : <p>There are no dancers that have orderd merchandise</p>}
                    </div>
                </div>
            </div>
        )
    }
}

