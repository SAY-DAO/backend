from datetime import datetime

import pytest
from flask.json import jsonify

from say.config import configs
from tests.helper import BaseTestClass


USER_UPDATE_URL = '/api/v2/user/update/userId=%s'


class TestUpdateUser(BaseTestClass):
    def mockup(self):
        self.pw = '123456'
        self.user = self._create_random_user()

    # TODO: Write test for errors
    @pytest.mark.parametrize(
        'field,value,expected',
        [
            ('receiveEmail', False, 200),
            ('firstName', 'arash', 200),
            ('lastName', 'FZ', 200),
            # ('country', 'IR', 200), # FIXME: country is object and should be code
            ('city', 1, 200),
            ('postal_address', '1234567890', 200),
            ('postal_code', '1234567890', 200),
            ('birthPlace', 1, 200),
            ('locale', 'en', 200),
            ('birthDate', '1999-09-09', 200),
            ('birthDate', '1999-29-59', 400),
            ('gender', 'male', 200),
        ],
    )
    def test_user_update_me(self, field, value, expected):
        self.login(self.user)

        res = self.client.patch(
            USER_UPDATE_URL % 'me',
            data={
                field: value,
            },
        )
        assert res.status_code == expected
        if expected == 200:
            expected_value = value

            if field == 'birthDate':
                expected_value = jsonify(datetime.strptime(value, '%Y-%m-%d')).json

            assert res.json.get(field) == expected_value

    def test_user_update_me_avatar(self):
        self.login(self.user)
        res = self.client.patch(
            USER_UPDATE_URL % 'me',
            data={'avatarUrl': self.create_test_file('test.jpg')},
        )
        assert res.status_code == 200
        assert res.json.get('avatarUrl').startswith(configs.BASE_RESOURCE_URL)

        res = self.client.patch(
            USER_UPDATE_URL % 'me',
            data={'avatarUrl': self.create_test_file('test.png')},
        )
        assert res.status_code == 200
        assert res.json.get('avatarUrl').startswith(configs.BASE_RESOURCE_URL)

        res = self.client.patch(
            USER_UPDATE_URL % 'me',
            data={'avatarUrl': self.create_test_file('test.mp3')},
        )
        assert res.status_code == 400
