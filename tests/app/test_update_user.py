from datetime import datetime

import pytest
from flask.json import jsonify

from tests.helper import BaseTestClass


USER_UPDATE_URL = '/api/v2/user/update/userId=%s'


class TestUpdateUser(BaseTestClass):
    def mockup(self):
        self.pw = '123456'
        self.user = self._create_random_user(password=self.pw)

    @pytest.mark.parametrize(
        'field,value,expected',
        [
            ('receiveEmail', False, 200),
            ('firstName', 'arash', 200),
            ('lastName', 'FZ', 200),
            ('country', 'ir', 200),
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
        self.login(self.user.userName, self.pw)

        res = self.client.patch(
            USER_UPDATE_URL % 'me',
            data={
                field: value,
            },
        )
        assert res.status_code == expected
        if expected == 200:
            expected_value = res.json.get(field)

            if field == 'birthDate':
                expected_value = jsonify(datetime.strptime(value, '%Y-%m-%d')).json

            assert res.json.get(field) == expected_value
