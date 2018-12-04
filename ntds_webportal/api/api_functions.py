import functools


def deep_setattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(deep_getattr(obj, pre) if pre else obj, post, val)


def deep_getattr(deep_obj, deep_attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [deep_obj] + deep_attr.split('.'))


def contestant_api_filter(data_dict, api_call):
    if len(api_call) == 0:
        return data_dict
    for key in api_call:
        data_dict = data_dict[key]
    return data_dict


def contestant_api_id_filter(api_call):
    api_call = api_call.strip("/").split("/")
    try:
        return int(api_call[0]), api_call[1:]
    except ValueError:
        return 0, []
