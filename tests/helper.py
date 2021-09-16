import tempfile
from datetime import datetime
from hashlib import md5
from os import name
from random import choice
from random import randint

import pytest

from say.config import configs
from say.models import Child
from say.models import Family
from say.models import Need
from say.models import Ngo
from say.models import Privilege
from say.models import SocialWorker
from say.models import User
from say.models import UserFamily
from say.models.cart import Cart
from say.roles import SUPER_ADMIN


LOGIN_URL = '/api/v2/auth/login'
PANEL_LOGIN_URL = '/api/v2/panel/auth/login'

UNAUTHORIZED_ERROR_CODE = 401

REFRESH_TOKEN_KEY = 'REFRESH_TOKEN'


class BaseTestClass:
    _authorization__ = None

    @pytest.fixture(scope='function', autouse=True)
    def init_class(self, db, client):
        configs.UPLOAD_FOLDER = tempfile.mkdtemp()
        configs.TESTING = True

        # DBSession
        self.session = db()

        # Insert mockup data
        self.mockup()

        # Disable Sentry
        import sentry_sdk
        sentry_sdk.init()

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
            name=SUPER_ADMIN,
            privilege=0  # Social Worker
        )
        self.session.save(privilege)
        social_worker = SocialWorker(
            id=seed,
            generatedCode=seed,
            lastName=f'test{seed}',
            userName=f'test{seed}',
            password=password,
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
            phone_number=f'+9899{seed}',
            is_phonenumber_verified=True,
            password=password,
            firstName=f'test{seed}',
            lastName=f'test{seed}',
            city=1,
            country=1,
            lastLogin=datetime.utcnow(),
            cart=Cart(),
        )
        return user

    def _create_user_family(self, user=None):
        family = self._create_random_family()
        user = user or self.create_user()

        user_family = UserFamily(
            user=user,
            family=family,
            userRole=0,
        )
        self.session.save(user_family)
        return user_family

    def _create_random_need(self, child=None, confirmed=True, **kwargs):
        child = child or self._create_random_child()
        seed = randint(1, 10 ** 3)
        randomstr = str(seed)
        data = dict(
            child=child,
            name=randomstr,
            description=randomstr,
            imageUrl=randomstr,
            category=0,
            _cost=seed,
            purchase_cost=seed,
            isConfirmed=confirmed,
            confirmUser=child.id_social_worker,
            type=1,
            confirmDate=confirmed and datetime.utcnow(),
            isUrgent=False,
        )
        data.update(kwargs)
        need = Need(**data)
        self.session.save(need)
        return need

    def _create_random_family(self):

        child = self._create_random_child()
        family = Family(
            child=child,
        )
        self.session.save(family)
        return family

    def _create_random_child(self):
        seed = randint(1, 10 ** 3)
        randomstr = str(seed)
        sw = self._create_random_sw()
        child = Child(
            ngo=sw.ngo,
            social_worker=sw,
            firstName=randomstr,
            lastName=randomstr,
            sayName=randomstr,
            phoneNumber=randomstr,
            country=seed,
            city=seed,
            awakeAvatarUrl=randomstr,
            sleptAvatarUrl=randomstr,
            gender=False,
            bio=randomstr,
            bioSummary=randomstr,
            voiceUrl=randomstr,
            generatedCode=randomstr,
            isConfirmed=choice([True, False]),
        )
        self.session.save(sw)
        return child

    def _create_random_sw(self):
        seed = randint(1, 10 ** 3)
        ngo = self._create_random_ngo()
        sw = SocialWorker(
            ngo=ngo,
            generatedCode=str(seed),
            firstName=str(seed),
            lastName=str(seed),
            userName=str(seed),
            idNumber=str(seed),
            gender=False,
            emergencyPhoneNumber=str(seed),
            telegramId=str(seed),
            avatarUrl=str(seed),
            emailAddress=f'{str(seed)}@email.com',
            phoneNumber=str(seed),
            password='abc',
            registerDate=datetime.utcnow(),
            lastLoginDate=datetime.utcnow(),
            privilege=Privilege(
                name='admin',
                privilege=1
            ),
        )
        self.session.save(sw)
        return sw

    def _create_random_ngo(self):
        seed = randint(1, 10 ** 3)
        ngo = Ngo(
            country=0,
            city=0,
            name=str(seed),
            emailAddress=f'{str(seed)}@email.com',
            phoneNumber=str(seed),
            logoUrl='',
            postalAddress=str(seed),
            registerDate=datetime.utcnow()
        )
        self.session.save(ngo)
        return ngo

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

    def login_sw(self, username, password):
        res = self.client.post(
            PANEL_LOGIN_URL,
            data={
                'username': username,
                'password': password,
            },
        )
        assert res.status_code == 200
        assert (token := res.json['access_token']) is not None
        assert (refreshToken := res.json['refresh_token']) is not None
        self._client.environ_base['HTTP_AUTHORIZATION'] = token
        self._client.environ_base[REFRESH_TOKEN_KEY] = refreshToken
        return token

