GROUP_MATCHED = 'Complete group: {}'
GROUP_NO_PARTNER = 'Incomplete group: {}\n\tTemporarily removing from selection'
TEAMCAPTAIN_EXCEPTION = 'Selected {} alone because he/she is a teamcaptain'


def string_group(group_list, base_string):
    g = [d.get_full_name() for d in group_list]
    g = ', '.join(g)
    return base_string.format(g)


def string_group_matched(group_list):
    return string_group(group_list, GROUP_MATCHED)


def string_group_no_partner(group_list):
    return string_group(group_list, GROUP_NO_PARTNER)
