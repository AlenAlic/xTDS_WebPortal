from werkzeug.routing import BaseConverter
import string
import random


def str2bool(v):
    return v in (str(True))


def random_password():
    allowed_chars = string.ascii_letters + '0123456789'
    return ''.join(random.sample(allowed_chars, 12))


def uniquify(seq):
    s = set(seq)
    s = list(s)
    s.sort()
    return s if len(seq) > 0 else []


def hours_delta(td):
    seconds = td.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f'{"{:02d}".format(int(hours))}:{"{:02d}".format(int(minutes))}'


class BooleanConverter(BaseConverter):

    def to_python(self, value):
        return bool(int(value))

    def to_url(self, value):
        return str(int(value))
