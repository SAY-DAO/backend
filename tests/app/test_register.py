from random import randint

import pytest

from tests.helper import BaseTestClass


REGISTER_URL = '/api/v2/auth/register'


class TestRegister(BaseTestClass):
    def mockup(self):
        seed = randint(10 ** 6, 10 ** 8)
        self.phone = '+98999999'
        self.email = 'test@test.com'
        self.phone_verification = self._create_phone_verification(
            phone_number=self.phone,
        )
        self.email_verification = self._create_email_verification(
            email=self.email,
        )
        self.data = {
            'username': seed,
            'password': 'password',
            'phoneNumber': self.phone,
            'countryCode': 'ir',
            'verifyCode': self.phone_verification._code,
            'isInstalled': '0',
        }

    def test_register_user_by_phone(self):

        # Phone is not verified
        res = self.client.post(REGISTER_URL, data=self.data)
        assert res.status_code == 400

        # Phone is verified
        self.phone_verification.verified = True
        self.session.save(self.phone_verification)

        res = self.client.post(
            REGISTER_URL,
            data={**self.data, 'verifyCode': 'invalid'},
        )
        assert res.status_code == 400

        res = self.client.post(
            REGISTER_URL,
            data={
                **self.data,
                'verifyCode': self.phone_verification._code[:3]
                + '-'
                + self.phone_verification._code[3:],
            },
        )
        assert res.status_code == 200

        # Phone exists
        res = self.client.post(REGISTER_URL, data=self.data)
        assert res.status_code == 422

    def test_register_user_by_email(self):
        del self.data['phoneNumber']
        self.data['email'] = self.email

        # Email is not verified
        res = self.client.post(REGISTER_URL, data=self.data)
        assert res.status_code == 400

        # Email is invalid
        res = self.client.post(REGISTER_URL, data={**self.data, 'email': '@test.com'})
        assert res.status_code == 400

        res = self.client.post(REGISTER_URL, data={**self.data, 'email': 'test@test'})
        assert res.status_code == 400

        res = self.client.post(REGISTER_URL, data={**self.data, 'email': 'test@.com'})
        assert res.status_code == 400

        # Email is verified
        self.email_verification.verified = True
        self.session.save(self.email_verification)

        res = self.client.post(
            REGISTER_URL,
            data={**self.data, 'verifyCode': 'invalid'},
        )
        assert res.status_code == 400

        res = self.client.post(
            REGISTER_URL,
            data={
                **self.data,
                'verifyCode': self.email_verification._code[:3]
                + '-'
                + self.email_verification._code[3:],
            },
        )
        assert res.status_code == 200

        # Email exists
        res = self.client.post(REGISTER_URL, data=self.data)
        assert res.status_code == 422

    @pytest.mark.parametrize(
        'field,value,expected',
        [
            ('phoneNumber', None, 400),
            ('phoneNumber', '', 400),
            ('phoneNumber', '9898123213', 400),
            ('username', 'a', 400),
            ('username', 'abc.def', 200),
            ('username', '.abcdef', 400),
            # ('username', '1abcdef', 400),  # Fixed but not merged, https://github.com/SAY-DAO/backend/issues/27
            # ('username', 'abcdef.', 400),  # Fixed but not merged, https://github.com/SAY-DAO/backend/issues/27
            ('username', 'abcdef@', 400),
            ('username', 'abcdef$', 400),
            ('username', 'abcdef#', 400),
            ('username', 'abcdef*', 400),
            ('username', 'abcdef&', 400),
            ('username', 'abcdef!', 400),
            ('username', 'abcdef%', 400),
            ('username', 'abcdef(', 400),
            ('username', 'a' * 13, 400),
            ('password', 'a' * 5, 400),
            ('password', 'a' * 65, 400),
            ('countryCode', None, 200),
            ('countryCode', '', 200),
            ('countryCode', 'axsda', 400),
            ('countryCode', 'ca', 200),
        ],
    )
    def test_register_user_invalid_data(self, field, value, expected):
        self.phone_verification.verified = True
        self.session.save(self.phone_verification)

        res = self.client.post(REGISTER_URL, data={**self.data, field: value})
        assert res.status_code == expected
