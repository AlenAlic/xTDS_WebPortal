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
    SELECTION_BUFFER: 20,
    MAX_TEAMCAPTAINS: 1
}

raffle_config_items = [MAX_DANCERS, SELECTION_BUFFER]

raffle_labels = {
    MAX_DANCERS: 'The maximum number of dancers that will be let into the tournament.',
    MIN_TEAM_BEGINNERS: 'The number of Beginners that each team will get guaranteed.',
    MIN_LIONS: 'The number of Lion/Mouse contestants that each team will get guaranteed.',
    BEGINNERS_CUTOFF: 'The cutoff number for selecting all Beginners. If less than this amount of Beginners have '
                      'signed up, all off them will be selected during the raffle.',
    SELECTION_BUFFER: 'The number of spots that will be left at the end of the main raffle.',
    MAX_TEAMCAPTAINS: 'The number of team captains that will be allowed per team.'
}

