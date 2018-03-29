MAX_DANCERS = 'max_dancers'
MIN_TEAM_BEGINNERS = 'min_team_beginners'
MIN_LIONS = 'min_lions'
BEGINNERS_CUTOFF = 'beginners_cutoff'
SELECTION_BUFFER = 'selection_buffer'
MAX_TEAMCAPTAINS = 'max_teamcaptains'

raffle_settings = {
    MAX_DANCERS: 300,
    MIN_TEAM_BEGINNERS: 0,
    MIN_LIONS: 0,
    BEGINNERS_CUTOFF: 0,
    SELECTION_BUFFER: 0,
    MAX_TEAMCAPTAINS: 1
}

raffle_settings[SELECTION_BUFFER] = int(raffle_settings[MAX_DANCERS]*(100-raffle_settings[SELECTION_BUFFER])/100)
