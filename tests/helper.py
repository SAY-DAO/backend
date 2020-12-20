import tempfile
from datetime import datetime
from hashlib import md5
from random import randint

import pytest

from say.config import configs
from say.models import User, SocialWorker, Privilege, Ngo
from tests.conftest import TEST_DB_URL

LOGIN_URL = '/api/v2/auth/login'

UNAUTHORIZED_ERROR_CODE = 401

REFRESH_TOKEN_KEY = 'REFRESH_TOKEN'


class BaseTestClass:
    _authorization__ = None

    @pytest.fixture(scope='function', autouse=True)
    def init_class(self, db, client):
        configs.dbUrl = TEST_DB_URL
        configs.UPLOAD_FOLDER = tempfile.mkdtemp()
        configs.TESTING = True

        # DBSession
        self.session = db()

        # Insert mockup data
        self.mockup()

        # get client
        self._client = client

    @property
    def client(self):
        return self._client

    def mockup(self):
        # Override this method to add mockup data
        pass

    def create_panel_user(self, password='password'):
        seed = randint(10 ** 3, 10 ** 4)
        ngo = Ngo(
            id=seed,
            country=1,
            city=1,
            name=f'test{seed}',
            postalAddress=f'test{seed}',
            emailAddress=f'{seed}test@test.com',
            phoneNumber='09127616539',
            website=f'test{seed}',
            logoUrl='',
            balance=0,
            socialWorkerCount=1,
            currentSocialWorkerCount=1,
            childrenCount=2,
            currentChildrenCount=1,
            registerDate=datetime.utcnow(),
            isActive=1,
            isDeleted=0
        )
        self.session.save(ngo)
        privilege = Privilege(
            id=seed,
            name=f'{seed}',
            privilege=2  # Social Worker
        )
        self.session.save(privilege)
        social_worker = SocialWorker(
            id=seed,
            generatedCode=seed,
            lastName=f'test{seed}',
            userName=f'test{seed}',
            password=md5(password.encode()).hexdigest(),
            avatarUrl='',
            emailAddress=f'{seed}test@test.com',
            phoneNumber='09121111111',
            gender=1,
            idNumber=f'{seed}',
            id_ngo=ngo.id,
            emergencyPhoneNumber='09124548745',
            telegramId='fuck',
            registerDate=datetime.utcnow(),
            lastLoginDate=datetime.utcnow(),
            id_type=privilege.id
        )
        self.session.save(social_worker)
        return social_worker

    def create_user(self, password='password'):
        user = self._create_random_user(password)
        self.session.save(user)
        return user

    def _create_random_user(self, password):
        seed = randint(10 ** 3, 10 ** 4)
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

    def logout(self):
        del self._client.environ_base['HTTP_AUTHORIZATION']

    def login(self, username, password, is_installed=1):
        res = self.client.post(
            LOGIN_URL,
            data={
                'username': username,
                'password': password,
                'isInstalled': is_installed,
            },
        )
        assert res.status_code == 200
        assert (token := res.json['accessToken']) is not None
        assert (refreshToken := res.json['refreshToken']) is not None
        self._client.environ_base['HTTP_AUTHORIZATION'] = token
        self._client.environ_base[REFRESH_TOKEN_KEY] = refreshToken
        return token
