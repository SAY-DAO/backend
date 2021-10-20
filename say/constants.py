import string


DEFAULT_AVATAR_URI = 'public/resources/img/default-avatar.png'
PAST_PARTICIPANT_ROLE = -1
SAY_ROLE = -2
NAKAMA_ROLE = -3
DIGIKALA_TITLE_SEP = {
    '-',
    'اثر',
    'بسته',
    'حجم',
    'سری',
    'طرح',
    'مدل',
    'مقدار',
    'وزن',
    'کد',
}
MAX_NEED_COST = 2147483647
ALPHABET = string.ascii_letters + string.digits
DEFAULT_CHILD_ID = 104  # TODO: Remove this after implementing pre needs

BEARER = 'Bearer '
REFRESH_TOKEN_USER_PREFIX = 'user_'
REFRESH_TOKEN_SW_PREFIX = 'sw_'
SAY_USER = 'SAY'
