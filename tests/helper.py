import tempfile
from datetime import datetime
from random import choice
from random import randint

import pytest
import sqlalchemy

from say.api.payment_api import generate_order_id
from say.authorization import create_sw_access_token
from say.authorization import create_sw_refresh_token
from say.authorization import create_user_access_token
from say.authorization import create_user_refresh_token
from say.config import configs
from say.models import Child
from say.models import EmailVerification
from say.models import Family
from say.models import Need
from say.models import Ngo
from say.models import Payment
from say.models import PhoneVerification
from say.models import Privilege
from say.models import Receipt
from say.models import SocialWorker
from say.models import User
from say.models import UserFamily
from say.models.cart import Cart
from say.models.cart import CartNeed
from say.models.receipt import NeedReceipt
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
            isDeleted=0,
        )
        self.session.save(ngo)
        privilege = Privilege(id=seed, name=SUPER_ADMIN, privilege=0)  # Social Worker
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
            id_type=privilege.id,
        )
        self.session.save(social_worker)
        return social_worker

    def _create_random_cart(self, user=None, **kwargs):
        user = user or self._create_random_user()
        data = dict(
            user=user,
        )
        data.update(kwargs)
        cart = Cart(**data)
        self.session.save(cart)
        return cart

    def _create_random_user(self, **kwargs):
        seed = randint(10 ** 10, 10 ** 12)
        while True:
            try:
                data = dict(
                    userName=seed,
                    emailAddress=f'{seed}test@test.com',
                    phone_number=f'+9899{seed}',
                    is_phonenumber_verified=True,
                    password='password',
                    firstName=f'test{seed}',
                    lastName=f'test{seed}',
                    avatarUrl=str(seed),
                    city=1,
                    country=1,
                    lastLogin=datetime.utcnow(),
                    cart=Cart(),
                )
                data.update(kwargs)
                user = User(**data)
                self.session.save(user)
                return user
            except sqlalchemy.exc.IntegrityError:
                continue

    def _create_random_cart_need(self, cart=None, need=None, **kwargs):
        need = need or self._create_random_need()
        cart = cart or self._create_random_cart()

        data = dict(
            need=need,
            cart=cart,
        )
        data.update(kwargs)
        cart_need = CartNeed(**data)
        self.session.save(cart_need)
        return cart_need

    def _create_user_family(self, user=None, family=None):
        family = family or self._create_random_family()
        user = user or self._create_random_user()
        user_family = UserFamily(
            user=user,
            family=family,
            userRole=2,
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

    def _create_random_receipt(self, owner=None, **kwargs):
        owner = owner or self._create_random_sw()

        seed = randint(1, 10 ** 3)
        randomstr = str(seed)
        data = dict(
            owner=owner,
            attachment=randomstr,
            title=randomstr,
        )
        data.update(kwargs)
        receipt = Receipt(**data)
        self.session.save(receipt)
        return receipt

    def _create_need_receipt(self, need=None, sw=None, receipt=None, **kwargs):
        need = need or self._create_random_need()
        sw = sw or self._create_random_sw()
        receipt = receipt or self._create_random_receipt()
        data = dict(
            need=need,
            sw=sw,
            receipt=receipt,
        )
        data.update(kwargs)
        need_receipt = NeedReceipt(**data)
        self.session.save(need_receipt)
        return need_receipt

    def _create_random_family(self, child=None, members=[]):
        family = None

        if child is None:
            family = self._create_random_child().family
        else:
            family = Family(child=child)

        family.members = [UserFamily(user=user, userRole=2) for user in members]
        self.session.save(family)
        return family

    def _create_random_child(self, **kwargs):
        seed = randint(1, 10 ** 3)
        randomstr = str(seed)
        sw = self._create_random_sw()
        data = dict(
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
            birthDate=datetime.utcnow(),
            voiceUrl=randomstr,
            generatedCode=randomstr,
            isConfirmed=choice([True, False]),
            family=Family(),
        )
        data.update(kwargs)
        child = Child(**data)
        self.session.save(child)
        return child

    def _create_random_sw(self, role=SUPER_ADMIN, ngo=None, **kwargs):
        seed = randint(1, 10 ** 3)
        ngo = ngo or self._create_random_ngo()

        data = dict(
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
            password='abcefg123',
            registerDate=datetime.utcnow(),
            lastLoginDate=datetime.utcnow(),
            privilege=Privilege(name=role, privilege=1),
        )
        data.update(kwargs)
        sw = SocialWorker(**data)
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
            registerDate=datetime.utcnow(),
        )
        self.session.save(ngo)
        return ngo

    def _create_phone_verification(self, **kwargs):
        seed = randint(1, 10 ** 3)
        data = dict(
            phone_number=f'+9899{seed}',
        )
        data.update(kwargs)
        phone_verification = PhoneVerification(**data)
        self.session.save(phone_verification)
        return phone_verification

    def _create_email_verification(self, **kwargs):
        seed = randint(1, 10 ** 3)
        data = dict(
            email=f'{seed}@test.test',
        )
        data.update(kwargs)
        email_verification = EmailVerification(**data)
        self.session.save(email_verification)
        return email_verification

    def _create_payment(self, need=None, user=None, **kwargs):
        need = need or self._create_random_need()
        user = user or self._create_random_user()
        data = dict(
            user=user,
            need=need,
            need_amount=need.cost - need.paid,
            donation_amount=0,
            credit_amount=0,
            desc='',
            order_id=generate_order_id(),
            verified=datetime.utcnow(),
        )
        data.update(**kwargs)
        payment = Payment(**data)
        self.session.save(payment)
        return payment

    def logout(self):
        del self._client.environ_base['HTTP_AUTHORIZATION']

    def login(self, user):
        _user = user or self._create_random_user()

        with self.client.application.app_context():
            access_token = create_user_access_token(_user)
            refresh_token = create_user_refresh_token(user)

        self._client.environ_base['HTTP_AUTHORIZATION'] = access_token
        self._client.environ_base[REFRESH_TOKEN_KEY] = refresh_token
        return access_token

    def login_sw(self, sw=None):
        _sw = sw or self._create_random_sw()

        with self.client.application.app_context():
            access_token = create_sw_access_token(_sw)
            refresh_token = create_sw_refresh_token(_sw)

        self._client.environ_base['HTTP_AUTHORIZATION'] = access_token
        self._client.environ_base[REFRESH_TOKEN_KEY] = refresh_token
        return access_token

    def login_as_sw(self, role=SUPER_ADMIN):
        sw = self._create_random_sw(role=role)
        self.login_sw(sw)
        return sw

    def login_as_user(self):
        user = self._create_random_user()
        self.login(user)
        return user
