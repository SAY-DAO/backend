import secrets
import string

from .timed_lru_cache import timed_lru_cache


def surname(gender):
    surname = ''

    if gender is False:
        surname = 'سرکار خانم'
    else:
        surname = 'جناب اقای'

    return surname


def clean_input(input: str):
    return input.strip()


def random_string(length=10, letters=None):
    letters = letters or string.ascii_letters + string.digits
    return ''.join(secrets.choice(letters) for i in range(length))
