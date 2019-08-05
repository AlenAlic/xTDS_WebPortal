class PresenterAccordionCard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {collapsed: true};

        this.toggle = this.toggle.bind(this);
    }
    toggle() {
        this.setState({collapsed: !this.state.collapsed});
    }

    render() {
        return (
            <div className="card mb-0">
                <div className="card-header">
                    <span>{this.props.cardTitle}</span>
                    {this.props.counter  ? <span className={`badge mx-2 ${this.props.counter.x === this.props.counter.total ? "badge-success" : "badge-dark"}`}>{this.props.counter.x} / {this.props.counter.total}</span> : null}
                    {this.props.loading ? <span className="spinner-border spinner-border-sm mx-2" role="status"/> : null}
                    <span className={`float-right ${this.state.collapsed ? "collapsed" : ""} clickable`} onClick={this.toggle}>
                        <span className="border border-dark rounded px-3 py-1">
                            {this.state.collapsed ? <i className="fas fa-chevron-circle-down"/> : <i className="fas fa-chevron-circle-up"/>}
                        </span>
                    </span>
                </div>
                <div className={`collapse ${this.state.collapsed ? "" : "show"}`} data-parent={`#${this.props.accordion}`}>
                    <div className="card-body">
                        {this.props.children}
                    </div>
                </div>
            </div>
        )
    }
}

const QUALIFICATION = "qualification";
const GENERAL_LOOK = "general_look";
const FIRST_ROUND = "first_round";
const SECOND_ROUND = "second_round";
const RE_DANCE = "re_dance";
const INTERMEDIATE_ROUND = "intermediate_round";
const EIGHT_FINAL = "eight_final";
const QUARTER_FINAL = "quarter_final";
const SEMI_FINAL = "semi_final";
const FINAL = "final";
const updatePresentCouples = [QUALIFICATION, GENERAL_LOOK, FIRST_ROUND, SECOND_ROUND, RE_DANCE, INTERMEDIATE_ROUND,
    EIGHT_FINAL, QUARTER_FINAL, SEMI_FINAL];
const dontUpdatePresentCouples = [FINAL];

const CHANGE_PER_ROUND = "change_per_round";
const CHANGE_PER_DANCE = "change_per_dance";
const CHANGE_MODES = [CHANGE_PER_ROUND, CHANGE_PER_DANCE];


const StartingList = ({startingList, selectedRound}) => {
    return (
        startingList.map(d => (
            <div key={`number-${d.number}`}>
                <b>{d.number}</b> - {d.name}{selectedRound.type === FINAL ? ` (${d.team})` : null}
            </div>
        ))
    )
};
const DancersList = ({list, selectedRound}) => {
    return(
        CHANGE_MODES.includes(selectedRound.mode) ?
        <div className="d-grid grid-template-columns-2 grid-column-gap-2">
            <div>
                <h4>Leads</h4>
                <StartingList startingList={list.leads} selectedRound={selectedRound} />
            </div>
            <div>
                <h4>Follows</h4>
                <StartingList startingList={list.follows} selectedRound={selectedRound} />
            </div>
        </div>
        :
        <div>
            <StartingList startingList={list} selectedRound={selectedRound} />
        </div>
    )
};


const UPDATE_INTERVAL = 3000;


class PresenterWindow extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            rounds: [],
            selectedRound: null,

            adjudicators: null,
            loadingAdjudicators: false,
            updateAdjudicators: false,

            startingList: null,
            loadingStartingList: false,

            couplesPresent: null,
            loadingCouplesPresent: false,
            updateCouplesPresent: false,

            noReDanceList: null,
            loadingNoReDanceList: false,

            finalResult: null,
            loadingFinalResult: false
        };
        this.changeRound = this.changeRound.bind(this);
        this.refresh = this.refresh.bind(this);

        this.controller = new AbortController();
        this.signal = this.controller.signal;
    }

    componentDidMount() {
        this.getRounds(true);
        this.intervalCouplesPresent = setInterval(() => {
            this.state.selectedRound !== null && !this.state.selectedRound.completed &&
            this.state.updateCouplesPresent ? this.getCouplesPresent(this.state.selectedRound.id) : null
        }, UPDATE_INTERVAL);
        this.intervalAdjudicators = setInterval(() => {
            this.state.selectedRound !== null && !this.state.selectedRound.completed && this.state.adjudicators !== null &&
            this.state.updateAdjudicators ? this.getAdjudicators(this.state.selectedRound.id) : null
        }, UPDATE_INTERVAL);
    }
    componentWillUnmount() {
        clearInterval(this.intervalCouplesPresent);
        clearInterval(this.intervalAdjudicators);
        this.controller.abort()
    }

    getRounds(changeRound=false) {
        fetch("/adjudication_system/api/presenter/competition/"+ this.props.competition.id + "/rounds", {method: "GET", credentials: 'same-origin', signal: this.signal})
            .then(response => response.json())
            .then(result => {
                if (changeRound) {
                    let selectedRound = result.reduce((p, c) => {return p.id > c.id ? p : c});
                    this.setState({rounds: result, selectedRound: selectedRound});
                    this.setData(selectedRound)
                } else {
                    this.setState({rounds: result});
                    this.setData(this.state.selectedRound)
                }
            })
            .catch(() => {});
    }
    changeRound(event) {
        let selectedRound = this.state.rounds.find(r => {return r.id === Number(event.target.value)});
        this.setState({selectedRound: selectedRound});
        this.setData(selectedRound);
    }

    setData(selectedRound) {
        this.getCouplesPresent(selectedRound.id);
        this.getStartingList(selectedRound.id);
        this.getAdjudicators(selectedRound.id);
        {selectedRound.type === RE_DANCE ? this.getNoReDanceCouples(selectedRound.id) : null}
        {selectedRound.type === FINAL ? this.getFinalResult(selectedRound.id) : null}
    }
    refresh() {
       this.getRounds()
    }

    getAdjudicators(id) {
        this.setState({loadingAdjudicators: true});
        fetch("/adjudication_system/api/presenter/round/" + id + "/adjudicators", {method: "GET", credentials: 'same-origin', signal: this.signal})
            .then(response => response.json())
            .then(result => {
                this.setState({
                    adjudicators: result,
                    loadingAdjudicators: false,
                    updateAdjudicators: result.map(a => a.present).includes(false)
                });
            })
            .catch(() => {this.setState({loadingAdjudicators: false});});
    }
    getStartingList(id) {
        this.setState({loadingStartingList: true});
        fetch("/adjudication_system/api/presenter/round/" + id + "/starting_list", {method: "GET", credentials: 'same-origin', signal: this.signal})
            .then(response => response.json())
            .then(result => {this.setState({startingList: result, loadingStartingList: false});})
            .catch(() => {this.setState({loadingStartingList: false});});
    }
    getCouplesPresent(id) {
        this.setState({loadingCouplesPresent: true});
        fetch("/adjudication_system/api/presenter/round/" + id + "/couples_present", {method: "GET", credentials: 'same-origin', signal: this.signal})
            .then(response => response.json())
            .then(result => {
                this.setState({
                    couplesPresent: result.sort((a,b) => {return a.order-b.order}),
                    updateCouplesPresent: this.state.selectedRound.type !== "final",
                    loadingCouplesPresent: false
                });
            }).catch(() => {this.setState({loadingCouplesPresent: false});});
    }
    getNoReDanceCouples(id) {
        this.setState({loadingNoReDanceList: true});
        fetch("/adjudication_system/api/presenter/round/" + id + "/no_redance_couples", {method: "GET", credentials: 'same-origin', signal: this.signal})
            .then(response => response.json())
            .then(result => {this.setState({noReDanceList: result, loadingNoReDanceList: false});})
            .catch(() => {this.setState({loadingNoReDanceList: false});});
    }
    getFinalResult(id) {
        this.setState({loadingFinalResult: true});
        fetch("/adjudication_system/api/presenter/round/" + id + "/final_results", {method: "GET", credentials: 'same-origin', signal: this.signal})
            .then(response => response.json())
            .then(result => {this.setState({finalResult: result, loadingFinalResult: false});})
            .catch(() => {this.setState({loadingFinalResult: false});});
    }


    render() {
        const rounds = this.state.rounds;
        const selectedRound = this.state.selectedRound;

        const adjudicators = this.state.adjudicators;
        const startingList = this.state.startingList;
        const couplesPresent = this.state.couplesPresent;
        const noReDanceList = this.state.noReDanceList;
        const finalResult = this.state.finalResult;

        return (
            <React.Fragment>
                {selectedRound !== null &&
                    <div className="card">
                        <div className="px-2 py-2">
                            <h4 className="card-title">{this.props.competition.name}</h4>
                            <div className="form-group">
                                {/*<label htmlFor={`round-${this.props.competition.id}`}>Round</label>*/}
                                <select className="form-control" id={`round-${this.props.competition.id}`} value={selectedRound.id} onChange={this.changeRound}>
                                    {rounds.map(r => (
                                        <option value={r.id} key={`round-option-${r.id}`}>{r.name}</option>
                                    ))}
                                </select>
                                <div className="text-center mt-3">
                                    <button className="btn btn-dark" onClick={this.refresh}>Refresh</button>
                                </div>
                            </div>
                        </div>
                        <div className="px-2 pb-2">
                            {selectedRound !== null &&
                                <div className="accordion" id={`accordion-${selectedRound.id}`}>

                                    {/*{selectedRound.type === FINAL &&*/}
                                    {/*    <PresenterAccordionCard accordion={`accordion-${selectedRound.id}`} cardTitle="Final results" loading={this.state.loadingFinalResult}>*/}
                                    {/*        Final result*/}
                                    {/*    </PresenterAccordionCard>}*/}

                                    <PresenterAccordionCard accordion={`accordion-${selectedRound.id}`} cardTitle="Adjudicators" loading={this.state.loadingAdjudicators}
                                                            counter={adjudicators !== null ? {"x": adjudicators.filter(a => {return a.present === true}).length, "total": adjudicators.length} : adjudicators}>
                                        <div>
                                            {adjudicators !== null && adjudicators.map(a => (
                                                <div key={`adjudicator-${a.id}`}>
                                                    <span className={a.present ? "text-success": "text-danger"}>{a.name}</span>{!a.present ? ` (${a.round})` : null}
                                                </div>
                                            ))}
                                        </div>
                                    </PresenterAccordionCard>

                                    <PresenterAccordionCard accordion={`accordion-${selectedRound.id}`} cardTitle="Starting list" loading={this.state.loadingStartingList}>
                                        {startingList !== null && <DancersList list={startingList} selectedRound={selectedRound} />}
                                    </PresenterAccordionCard>

                                    {selectedRound.type === RE_DANCE &&
                                        <PresenterAccordionCard accordion={`accordion-${selectedRound.id}`} cardTitle="No re-dance" loading={this.state.loadingNoReDanceList}>
                                            {noReDanceList !== null && <DancersList list={noReDanceList} selectedRound={selectedRound} />}
                                        </PresenterAccordionCard>}

                                    {!dontUpdatePresentCouples.includes(selectedRound.type) &&
                                        <PresenterAccordionCard accordion={`accordion-${selectedRound.id}`} cardTitle="Couples present" loading={this.state.loadingCouplesPresent}>
                                            <div>
                                                {couplesPresent !== null && couplesPresent.map(d => (
                                                    <React.Fragment key={`dance-${d.id}`}>
                                                        <h5>{d.name}</h5>
                                                        <div className="mb-3">
                                                            {d.heats.map(h => (
                                                                <React.Fragment key={`heat-${h.id}`}>
                                                                    <h6>Heat {h.number}</h6>
                                                                    <div>{h.couples.map(c =>
                                                                        <b key={`couple-${c.number}`} className={`px-3 d-inline-block text-nowrap ${c.present ? "text-success" : "text-danger"}`}>{c.number}</b>
                                                                    )}</div>
                                                                </React.Fragment>
                                                            ))}
                                                        </div>
                                                    </React.Fragment>
                                                ))}
                                            </div>
                                        </PresenterAccordionCard>}

                                </div>}
                        </div>
                    </div>}
            </React.Fragment>
        );
    }
}