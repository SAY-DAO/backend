from datetime import datetime
from random import randint

import pytest

from say.models import User


class BaseTestClass:

    @pytest.fixture(scope='function', autouse=True)
    def init_class(self, db):
        self.session = db()
        self.mockup()

    def mockup(self):
        # Override this method to add mockup data
        pass

    def create_user(self, password='password'):
        user = self._create_random_user(password)
        self.session.save(user)
        return user

    def _create_random_user(self, password):
        seed = randint(10**3, 10**4)
        user = User(
            userName=seed,
            emailAddress=f'{seed}test@test.com',
            phone_number=f'+989990{seed}',
            password=password,
            firstName=f'test{seed}',
            lastName=f'test{seed}',
            city=1,
            country=1,
            lastLogin=datetime.utcnow(),
        )
        return user
