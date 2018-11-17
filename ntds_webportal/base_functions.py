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
