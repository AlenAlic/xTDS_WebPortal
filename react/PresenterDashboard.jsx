const maxTabs = 3;


class PresenterDashboard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            competitions: [],
            windows: []
        };
    }
    componentDidMount() {
        this.getCompetitions()
    }
    getCompetitions() {
        fetch("/adjudication_system/api/presenter/competition_list", {method: "GET", credentials: 'same-origin'})
            .then(response => response.json())
            .then(result => {
                result = Object.values(result).sort((a,b) => {return b.date-a.date});
                this.setState({competitions: result});
            })
    }
    getCompetitionsRounds(id) {
        fetch("/adjudication_system/api/presenter/competition_heat_list/"+id, {method: "GET", credentials: 'same-origin'})
            .then(response => response.json())
            .then(result => {
                result = Object.values(result).sort((a,b) => {return b.date-a.date});
                this.setState({competitions: result});
            })
    }
    numberOfTabs(event) {
        this.setState({tabs: Number(event.target.value)});
    }
    addCompetition(event, id) {
        let newWindows = this.state.windows;
        let competition = this.state.competitions.find(c => {return c.id === id});
        if (!newWindows.includes(competition) && newWindows.length < maxTabs) {
            if (newWindows.length === maxTabs) {newWindows.shift()}
            newWindows.push(competition)
        } else {
            newWindows = newWindows.filter(v => {return v !== competition})
        }
        this.setState({windows: newWindows})
    }

    render() {
        const competitions = this.state.competitions;
        const windows = this.state.windows;

        return (
            <React.Fragment>
                <h2>Add competitions to overview</h2>
                <div className="d-flex justify-content-between flex-wrap mb-3">
                    {competitions.map(c => (
                        <div className="form-group form-check mx-3" key={`competition-checkbox-${c.id}`}>
                            <input type="checkbox" className="form-check-input" id={`competition-checkbox-${c.id}`}
                                   value={c.id} onChange={e => this.addCompetition(e, c.id)} disabled={windows.length === maxTabs && !windows.includes(c)}/>
                            <label className="form-check-label clickable" htmlFor={`competition-checkbox-${c.id}`}>{c.name}</label>
                        </div>
                    ))}
                </div>
                <div className={`d-grid grid-column-gap-2 grid-template-columns-${windows.length}`}>
                    {windows.map(c => (
                        <PresenterWindow key={`competition-title-${c.id}`} competition={c} windows={windows.length}>{c.name}</PresenterWindow>
                    ))}
                </div>
            </React.Fragment>
        );
    }
}