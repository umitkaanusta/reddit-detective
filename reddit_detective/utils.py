import re


def strip_punc(str_):
    return re.sub(r"[^\w\s]", "", str_)
