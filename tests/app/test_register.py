from random import randint

from say.orm import session
from tests.helper import BaseTestClass


REGISTER_URL = '/api/v2/auth/register'


class TestRegister(BaseTestClass):

    def test_register_user(self):
        seed = randint(10 ** 3, 10 ** 4)
        res = self.client.post(
            REGISTER_URL,
            data={
                'username': seed,
                'password': 'password',
                'phoneNumber': '+98999999',
                'countryCode': 'ir',
                'email': f'{seed}test@test.com',
                'firstName': f'test{seed}',
                'lastName': f'test{seed}',
                'verifyCode': '123',
                'isInstalled': '0'
            }
        )
        print(res.status_code)

        assert res.status_code == 200
