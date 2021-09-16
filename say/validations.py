import re

import phonenumbers
from flask import Response
from flask.globals import request
from sqlalchemy_utils import PhoneNumber


VALID_ROLES = [*range(-1, 6)]

# TODO: Check the pattern with parsa and neda
USERNAME_PATTERN = r'[A-Za-z][.A-Za-z0-9]{5,11}$'
validate_username = re.compile(USERNAME_PATTERN).fullmatch

EMAIL_PATTERN = r'^[^@]+@[^@]+\.[^@]+$'
validate_email = re.compile(EMAIL_PATTERN).fullmatch

PASSWORD_PATTERN = '^([^\n ]{6,64})$'
validate_password = re.compile(PASSWORD_PATTERN).fullmatch

ALLOWED_VOICE_EXTENSIONS = {"wav", "m4a", "wma", "mp3", "aac", "ogg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_RECEIPT_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | {"pdf"}


def validate_phone(phone):
    try:
        return PhoneNumber(phone.replace(' ', ''))
    except phonenumbers.phonenumberutil.NumberParseException:
        return False


def validate(model):
    def wrapper(func):
        def inner(*_args, **_kwargs):
            try:
                request.model = model(**dict(request.form))
            except ValueError as e:
                return Response(
                    e.json(),
                    status=400,
                )
            return func(*_args, **_kwargs)
        return inner
    return wrapper


def allowed_voice(filename):
    if (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_VOICE_EXTENSIONS
    ):
        return True

    raise TypeError('Wrong voice format')


def allowed_image(filename):
    if (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    ):
        return True

    raise TypeError('Wrong image format')


def allowed_receipt(filename):
    if (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_RECEIPT_EXTENSIONS
    ):
        return True

    raise TypeError('Wrong receipt format')
