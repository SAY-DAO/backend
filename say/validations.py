import re
import phonenumbers
from sqlalchemy_utils import PhoneNumber


# TODO: Check the pattern with parsa and neda
USERNAME_PATTERN = r'^[a-zA-Z0-9_.]{4,12}$'
username_validator = re.compile(USERNAME_PATTERN).fullmatch

EMAIL_PATTERN = r'^[^@]+@[^@]+\.[^@]+$'
email_validator = re.compile(EMAIL_PATTERN).fullmatch


def phone_validator(phone):
    try:
        return PhoneNumber(phone.replace(' ', ''))
    except phonenumbers.phonenumberutil.NumberParseException:
        return False


