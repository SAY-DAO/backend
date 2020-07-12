from datetime import datetime
from random import randint

from say.models import User

TEST_DB_URL = 'postgresql://postgres:postgres@localhost/say_test'


def create_user(password='password'):
    seed = randint(100000, 9999999)
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
