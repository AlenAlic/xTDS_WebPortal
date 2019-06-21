class TeamCaptainFinances extends React.Component {
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
    allPayment(dancer) {
        this.setPending(dancer);
        let newState = this.state.dancers;
        fetch("/api/contestants/" + dancer.contestant_id +"/all_payment/" + Number(!dancer.payment_info.all_paid), {method: "PATCH", credentials: 'same-origin'})
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
    render() {
        const phdCategory = this.props.settings.phd_student_category;
        const merchandiseSold = this.props.settings.merchandise;

        const dancers = Object.values(this.state.dancers);

        const students = dancers.filter(filterStudents);
        const phdStudents = dancers.filter(filterPhDStudents);
        const nonStudents = dancers.filter(filterNonStudents);

        const studentsPaid = students.filter(filterEntryPaid);
        const phdStudentsPaid = phdStudents.filter(filterEntryPaid);
        const nonStudentsPaid = nonStudents.filter(filterEntryPaid);

        const studentsRemaining = students.length - studentsPaid.length;
        const phdStudentsRemaining = phdStudents.length - phdStudentsPaid.length;
        const nonStudentsRemaining = nonStudents.length - nonStudentsPaid.length;

        const studentsOwedPrice = students.map(mapEntryPrice).reduce(reduceArraySum, 0);
        const phdStudentsOwedPrice = phdStudents.map(mapEntryPrice).reduce(reduceArraySum, 0);
        const nonStudentsOwedPrice = nonStudents.map(mapEntryPrice).reduce(reduceArraySum, 0);

        const studentsPaidPrice = studentsPaid.map(mapEntryPrice).reduce(reduceArraySum, 0);
        const phdStudentsPaidPrice = phdStudentsPaid.map(mapEntryPrice).reduce(reduceArraySum, 0);
        const nonStudentsPaidPrice = nonStudentsPaid.map(mapEntryPrice).reduce(reduceArraySum, 0);

        const studentsRemainingPrice = studentsOwedPrice - studentsPaidPrice;
        const phdStudentsRemainingPrice = phdStudentsOwedPrice - phdStudentsPaidPrice;
        const nonStudentsRemainingPrice = nonStudentsOwedPrice - nonStudentsPaidPrice;

        const dancerOwed = dancers.length;
        const dancersPaid = studentsPaid.length + phdStudentsPaid.length + nonStudentsPaid.length;
        const dancersRemaining = dancerOwed - dancersPaid;

        const dancersOwedPrice = studentsOwedPrice + phdStudentsOwedPrice + nonStudentsOwedPrice;
        const dancersPaidPrice = studentsPaidPrice + phdStudentsPaidPrice + nonStudentsPaidPrice;
        const dancersRemainingPrice = dancersOwedPrice - dancersPaidPrice;

        const dancersWithMerchandise = dancers.filter(filterHasMerchandise);

        const merchandiseContainer = {};
        const merchandisePaidContainer = {};
        Object.values(this.props.merchandise_items).forEach(m => {
            merchandiseContainer[m.merchandise_item_id] = 0;
            merchandisePaidContainer[m.merchandise_item_id] = 0;
        });
        dancersWithMerchandise.forEach(d => Object.values(d.merchandise_info.purchases).forEach(p => merchandiseContainer[p.merchandise_item_id] += 1));
        dancersWithMerchandise.forEach(d => Object.values(d.merchandise_info.purchases).filter(filterHasMerchandisePaid).forEach(p => merchandisePaidContainer[p.merchandise_item_id] += 1));
        const merchandisePriceContainer = {};
        const merchandisePaidPriceContainer = {};
        Object.values(this.props.merchandise_items).forEach(m => {
            merchandisePriceContainer[m.merchandise_item_id] = merchandiseContainer[m.merchandise_item_id] * this.props.merchandise_items[m.merchandise_item_id].price;
            merchandisePaidPriceContainer[m.merchandise_item_id] = merchandisePaidContainer[m.merchandise_item_id] * this.props.merchandise_items[m.merchandise_item_id].price;
        });

        const merchandiseOwed = arrSum(Object.values(merchandiseContainer));
        const merchandisePaid = arrSum(Object.values(merchandisePaidContainer));
        const merchandiseRemaining = merchandiseOwed - merchandisePaid;

        const merchandiseOwedPrice = arrSum(Object.values(merchandisePriceContainer));
        const merchandisePaidPrice = arrSum(Object.values(merchandisePaidPriceContainer));
        const merchandiseRemainingPrice = merchandiseOwedPrice - merchandisePaidPrice;

        return (
            <React.Fragment>
                <h2>Summary</h2>
                <table className="table table-sm">
                    <thead>
                    <tr className="finances-summary-row">
                        <th style={{width: '26%'}}>Dancers</th>
                        <th style={{width: '10%'}}>#</th>
                        <th style={{width: '8%'}}>Owed</th>
                        <th style={{width: '20%'}}>#</th>
                        <th style={{width: '10%'}}>Paid</th>
                        <th style={{width: '18%'}}>#</th>
                        <th style={{width: '8%'}}>Remaining</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr className="finances-summary-row">
                        <td>Students:</td>
                        <td>{students.length}</td>
                        <td>{currencyFormat(studentsOwedPrice)}</td>
                        <td>{studentsPaid.length}</td>
                        <td>{currencyFormat(studentsPaidPrice)}</td>
                        <td>{studentsRemaining}</td>
                        <td>{currencyFormat(studentsRemainingPrice)}</td>
                    </tr>
                    {phdCategory ?
                    <tr className="finances-summary-row">
                        <td>PhD-students:</td>
                        <td>{phdStudents.length}</td>
                        <td>{currencyFormat(phdStudentsOwedPrice)}</td>
                        <td>{phdStudentsPaid.length}</td>
                        <td>{currencyFormat(phdStudentsPaidPrice)}</td>
                        <td>{phdStudentsRemaining}</td>
                        <td>{currencyFormat(phdStudentsRemainingPrice)}</td>
                    </tr> : null}
                    <tr className="finances-summary-row">
                        <td>Non-students:</td>
                        <td>{nonStudents.length}</td>
                        <td>{currencyFormat(nonStudentsOwedPrice)}</td>
                        <td>{nonStudentsPaid.length}</td>
                        <td>{currencyFormat(nonStudentsPaidPrice)}</td>
                        <td>{nonStudentsRemaining}</td>
                        <td>{currencyFormat(nonStudentsRemainingPrice)}</td>
                    </tr>
                    {merchandiseSold ?
                        <React.Fragment>
                            <tr className="finances-summary-row">
                                <td className="text-right"><i>Subtotal</i></td>
                                <td><i>{dancerOwed}</i></td>
                                <td><i>{currencyFormat(dancersOwedPrice)}</i></td>
                                <td><i>{dancersPaid}</i></td>
                                <td><i>{currencyFormat(dancersPaidPrice)}</i></td>
                                <td><i>{dancersRemaining}</i></td>
                                <td><i>{currencyFormat(dancersRemainingPrice)}</i></td>
                            </tr>
                            <tr>
                                <td><b>Merchandise</b></td>
                                <td colSpan="6" />
                            </tr>
                            {Object.values(this.props.merchandise_items).sort(sortMerchandiseAlphabetically).map(m => (
                                <tr className="finances-summary-row" key={'row'+`${m.merchandise_item_id}`}>
                                    <td>{m.description}</td>
                                    <td>{merchandiseContainer[m.merchandise_item_id]}</td>
                                    <td>{currencyFormat(merchandiseContainer[m.merchandise_item_id]*m.price)}</td>
                                    <td>{merchandisePaidContainer[m.merchandise_item_id]}</td>
                                    <td>{currencyFormat(merchandisePaidContainer[m.merchandise_item_id]*m.price)}</td>
                                    <td>{merchandiseContainer[m.merchandise_item_id]-merchandisePaidContainer[m.merchandise_item_id]}</td>
                                    <td>{currencyFormat((merchandiseContainer[m.merchandise_item_id]-merchandisePaidContainer[m.merchandise_item_id])*m.price)}</td>
                                </tr>
                            ))}
                            <tr className="finances-summary-row">
                                <td className="text-right"><i>Subtotal</i></td>
                                <td><i>{merchandiseOwed}</i></td>
                                <td><i>{currencyFormat(merchandiseOwedPrice)}</i></td>
                                <td><i>{merchandisePaid}</i></td>
                                <td><i>{currencyFormat(merchandisePaidPrice)}</i></td>
                                <td><i>{merchandiseRemaining}</i></td>
                                <td><i>{currencyFormat(merchandiseRemainingPrice)}</i></td>
                            </tr>
                        </React.Fragment>
                        : null}
                    <tr className="finances-summary-row">
                        <td><b>Total</b></td>
                        <td/>
                        <td><b>{currencyFormat(dancersOwedPrice + merchandiseOwedPrice)}</b></td>
                        <td/>
                        <td><b>{currencyFormat(dancersPaidPrice + merchandisePaidPrice)}</b></td>
                        <td/>
                        <td><b>{currencyFormat(dancersRemainingPrice + merchandiseRemainingPrice)}</b></td>
                    </tr>
                    </tbody>
                </table>
                {this.props.settings.view_only ? null :
                    <React.Fragment>
                        <div className="mt-3 mb-4">
                            <h2>Received by organization:</h2>
                            <h4>{currencyFormat(this.props.prices.team)} / {currencyFormat(dancersOwedPrice + merchandiseOwedPrice)}</h4>
                        </div>
                        <form className="my-3" method="POST" encType="multipart/form-data" noValidate>
                            <input className="btn btn-primary" id="download_file" name="download_file" type="submit" value="Download list of all payments"/>
                        </form>
                    </React.Fragment>
                }
                <table className="table table-sm table-hover">
                    <thead>
                    <tr>
                        <th style={{width: '26%'}} className="font-size-4">Confirmed dancers</th>
                        <th style={{width: '10%'}} className="text-right">Entry fee</th>
                        <th style={{width: '8%'}} />
                        <th style={{width: '20%'}} className="text-right">Merchandise</th>
                        <th style={{width: '10%'}} />
                        <th style={{width: '8%'}} />
                        <th style={{width: '10%'}} className="text-right">Total</th>
                        <th style={{width: '8%'}} />
                    </tr>
                    <tr>
                        <th>Dancer</th>
                        <th className="text-right">Price</th>
                        <th className="text-right">Paid</th>
                        <th className="text-right">Item</th>
                        <th className="text-right">Price</th>
                        <th className="text-right">Paid</th>
                        <th className="text-right">Price</th>
                        <th className="text-right">Paid</th>
                    </tr>
                    </thead>
                    <tbody>
                    {dancers.filter(filterConfirmed).length > 0 ?
                        dancers.filter(filterConfirmed).sort(sortDancersAlphabetically).map( d => (
                            <tr className={d.pending ? "table-warning" : d.payment_info.all_paid ? "table-success": d.payment_info.partial_paid ? "table-info": ""} key={'row'+`${d.contestant_id}`}>
                                <td>{d.full_name}</td>
                                <td className="text-right">{currencyFormat(this.props.prices[d.contestant_info.student])}</td>
                                <td className="text-right">
                                    {this.props.settings.view_only ?
                                        <input type="checkbox" disabled defaultChecked={d.payment_info.entry_paid}/> :
                                        <input type="checkbox" onChange={() => this.entryPayment(d)} checked={d.payment_info.entry_paid}/>
                                    }
                                </td>
                                <td className="text-right">
                                    {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(p => (
                                        !p.cancelled ? <div key={'item'+`${p.merchandise_purchased_id}`}>{p.item}</div> : null
                                    )) : "-"}
                                </td>
                                <td className="text-right">
                                    {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(p => (
                                        !p.cancelled ? <div key={'price'+`${p.merchandise_purchased_id}`}>{currencyFormat(p.price)}</div> : null
                                    )) : "-"}
                                </td>
                                <td className="text-right">
                                    {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).sort(sortMerchandiseAlphabetically).map(p => (
                                        !p.cancelled ? <div key={'paid'+`${p.merchandise_purchased_id}`}>
                                            {this.props.settings.view_only ?
                                                <input type="checkbox" disabled defaultChecked={p.paid}/> :
                                                <input type="checkbox" onChange={() => this.merchandisePayment(d, p)} checked={p.paid}/>
                                            }
                                        </div> : null
                                    )) : "-"}
                                </td>
                                <td className="text-right">{currencyFormat(this.props.prices[d.contestant_info.student]+d.merchandise_info.merchandise_price)}</td>
                                <td className="text-right">
                                    {this.props.settings.view_only ?
                                        <input type="checkbox" disabled defaultChecked={d.payment_info.all_paid}/> :
                                        <input type="checkbox" onChange={() => this.allPayment(d)} checked={d.payment_info.all_paid}/>
                                    }
                                </td>
                            </tr>
                        )): <tr><td colSpan="8">There are no confirmed dancers with a payment requirement.</td></tr>}
                    </tbody>
                </table>
                <table className="table table-sm table-hover">
                    <thead>
                    <tr>
                        <th style={{width: '26%'}} className="font-size-4">Cancelled dancers</th>
                        <th style={{width: '10%'}} className="text-right">Entry fee</th>
                        <th style={{width: '8%'}} />
                        <th style={{width: '20%'}} className="text-right">Merchandise</th>
                        <th style={{width: '10%'}} />
                        <th style={{width: '8%'}} />
                        <th style={{width: '10%'}} className="text-right">Total</th>
                        <th style={{width: '8%'}} />
                    </tr>
                    <tr>
                        <th>Dancer</th>
                        <th className="text-right">Price</th>
                        <th className="text-right">Paid</th>
                        <th className="text-right">Item</th>
                        <th className="text-right">Price</th>
                        <th className="text-right">Paid</th>
                        <th className="text-right">Price</th>
                        <th className="text-right">Paid</th>
                    </tr>
                    </thead>
                    <tbody>
                    { dancers.filter(filterCancelled).length > 0 ?
                        dancers.filter(filterCancelled).sort(sortDancersAlphabetically).map( d => (
                            <tr className={d.pending ? "table-warning" : d.payment_info.all_paid ? "table-success": d.payment_info.partial_paid ? "table-info": ""} key={'row'+`${d.contestant_id}`}>
                                <td>{d.full_name}</td>
                                <td className="text-right">{currencyFormat(this.props.prices[d.contestant_info.student])}</td>
                                <td className="text-right">
                                    {this.props.settings.view_only ?
                                        <input type="checkbox" disabled defaultChecked={d.payment_info.entry_paid}/> :
                                        <input type="checkbox" onChange={() => this.entryPayment(d)} checked={d.payment_info.entry_paid}/>
                                    }
                                </td>
                                <td className="text-right">
                                    {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).filter(filterPurchaseNotCancelled).sort(sortMerchandiseAlphabetically).map(p => (
                                        <div key={'item'+`${p.merchandise_purchased_id}`}>{p.item}</div>
                                    )) : "-"}
                                </td>
                                <td className="text-right">
                                    {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).filter(filterPurchaseNotCancelled).sort(sortMerchandiseAlphabetically).map(p => (
                                        <div key={'price'+`${p.merchandise_purchased_id}`}>{currencyFormat(p.price)}</div>
                                    )) : "-"}
                                </td>
                                <td className="text-right">
                                    {Object.keys(d.merchandise_info.purchases).length > 0 ? Object.values(d.merchandise_info.purchases).filter(filterPurchaseNotCancelled).sort(sortMerchandiseAlphabetically).map(p => (
                                        <div key={'paid'+`${p.merchandise_purchased_id}`}>
                                            {this.props.settings.view_only ?
                                                <input type="checkbox" disabled defaultChecked={p.paid}/> :
                                                <input type="checkbox" onChange={() => this.merchandisePayment(d, p)} checked={p.paid}/>
                                            }
                                        </div>
                                    )) : "-"}
                                </td>
                                <td className="text-right">{currencyFormat(this.props.prices[d.contestant_info.student]+d.merchandise_info.merchandise_price)}</td>
                                <td className="text-right">
                                    {this.props.settings.view_only ?
                                        <input type="checkbox" disabled defaultChecked={d.payment_info.all_paid}/> :
                                        <input type="checkbox" onChange={() => this.allPayment(d)} checked={d.payment_info.all_paid}/>
                                    }
                                </td>
                            </tr>
                        )) : <tr><td colSpan="8">There are no dancers that have cancelled with a payment requirement.</td></tr>}
                    </tbody>
                </table>
                {dancers.filter(filterHasRefund).length > 0 ?
                    <table className="table table-sm mt-3">
                        <thead>
                        <tr>
                            <th className="font-size-4" colSpan="5">Refunds</th>
                        </tr>
                        <tr>
                            <th style={{width: '32%'}}>Dancer</th>
                            <th style={{width: '35%'}}>Refund</th>
                            <th style={{width: '15%'}} className="text-right">Amount</th>
                            <th style={{width: '10%'}} className="text-right">Total</th>
                            <th style={{width: '8%'}}/>
                        </tr>
                        </thead>
                        <tbody>
                        {dancers.filter(filterHasRefund).sort(sortDancersAlphabetically).map( (d, i) => (
                        <tr key={'row'+`${d.contestant_id}`}>
                            <td>{d.full_name}</td>
                            <td>{d.payment_info.refunds.map(r => (<div key={'reason-'+r.refund_id+`${d.contestant_id}`}>{r.reason}</div>))}</td>
                            <td className="text-right">{d.payment_info.refunds.map(r => (<div key={'price-'+r.refund_id+`${d.contestant_id}`}>{currencyFormat(r.amount)}</div>))}</td>
                            <td className="text-right">{currencyFormat(d.payment_info.refund_price)}</td>
                            <td/>
                        </tr>))}
                        </tbody>
                    </table>
                    : null}
            </React.Fragment>
        )
    }
}

