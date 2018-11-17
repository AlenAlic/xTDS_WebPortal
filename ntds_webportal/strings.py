GROUP_MATCHED = 'Complete group: {}'
GROUP_MATCHED_INCOMPLETE = 'Incomplete group: {}'
GROUP_NO_PARTNER = 'Incomplete group: {}\n\tTemporarily removing from selection'
TEAMCAPTAIN_EXCEPTION = 'Selected {} alone because he/she is a teamcaptain'
GUARANTEED_EXCEPTION = 'Selected {} alone because he/she is guaranteed entry by the organization'
NO_PARTNER = 'No partner available for: {}\n\tTemporarily removing from selection'
BEGINNER_EXCEPTION = 'Selected {} because he/she is a Beginner'
GROUP_MATCHED_INCOMPLETE_REDUCING_DIFFERENCE = 'Incomplete group: {}\n\tSelected due to difference reduction'
GROUP_MATCHED_INCOMPLETE_TEAM_CAPTAIN_EXCEPTION = 'Incomplete group: {}\n\tSelected due to team captain in group'
GROUP_MATCHED_INCOMPLETE_BEGINNERS_EXCEPTION = 'Incomplete group: {}\n\tSelected due to Beginners exception'
GROUP_MATCHED_INCOMPLETE_GENERAL_EXCEPTION = 'Incomplete group: {}\n\tSelected due to general exception'


def string_group(group, base_string):
    g = [d.get_full_name() for d in group.dancers]
    g = ', '.join(g)
    return base_string.format(g)


def string_group_matched(group):
    return string_group(group, GROUP_MATCHED)


def string_group_matched_incomplete(group):
    return string_group(group, GROUP_MATCHED_INCOMPLETE)


def string_group_no_partner(group):
    return string_group(group, GROUP_NO_PARTNER)


def string_group_matched_incomplete_reducing_difference(group):
    return string_group(group, GROUP_MATCHED_INCOMPLETE_REDUCING_DIFFERENCE)


def string_group_matched_incomplete_team_captain_exception(group):
    return string_group(group, GROUP_MATCHED_INCOMPLETE_TEAM_CAPTAIN_EXCEPTION)
