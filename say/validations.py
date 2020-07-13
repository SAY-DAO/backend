import re
import phonenumbers
from sqlalchemy_utils import PhoneNumber


VALID_ROLES = [*range(-1, 6)]

# TODO: Check the pattern with parsa and neda
USERNAME_PATTERN = r'[A-Za-z0-9][.A-Za-z0-9]{3,11}$'
validate_username = re.compile(USERNAME_PATTERN).fullmatch

EMAIL_PATTERN = r'^[^@]+@[^@]+\.[^@]+$'
validate_email = re.compile(EMAIL_PATTERN).fullmatch

PASSWORD_PATTERN = '^(.){6,64}$'
validate_password = re.compile(PASSWORD_PATTERN).fullmatch


def validate_phone(phone):
    try:
        return PhoneNumber(phone.replace(' ', ''))
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

