import os
import random

import pytest

from say import helpers
from say.helpers import get_secret
from say.helpers import strip_scheme
from say.helpers import to_camel


@pytest.mark.parametrize(
    'value, expected',
    [
        ('http://a.b', 'a.b'),
        ('https://a.b', 'a.b'),
        ('a.b', 'a.b'),
    ],
)
def test_strip_schema(value, expected):
    assert strip_scheme(value) == expected


@pytest.mark.parametrize(
    'value, expected',
    [
        ('a_b_cD_e', 'aBCdE'),
        ('ABC', 'abc'),
    ],
)
def test_to_camel(value, expected):
    assert to_camel(value) == expected


def test_get_secret(mocker, tmpdir):
    mocker.patch.object(helpers, 'SECRET_PATH', tmpdir)

    secret_name = 'secret-key'
    env_secret_name = 'SECRET_KEY'
    secret = str(random.random())
    secret_file_path = os.path.join(helpers.SECRET_PATH, secret_name)

    # Wihtout file or env
    assert get_secret(secret_name) is None

    # Wiht default
    assert get_secret(secret_name, default=secret) == secret

    # Wiht env
    os.environ[env_secret_name] = secret
    assert get_secret(secret_name) == secret

    secret = str(random.random())
    with open(secret_file_path, 'w') as secret_file:
        secret_file.write(secret)

    assert get_secret(secret_name) == secret
