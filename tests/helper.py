import io
import tempfile
from datetime import datetime
from random import choice
from random import randint

import pytest
import sqlalchemy

from say.api.ext import idpay
from say.api.payment_api import generate_order_id
from say.authorization import create_sw_access_token
from say.authorization import create_sw_refresh_token
from say.authorization import create_user_access_token
from say.authorization import create_user_refresh_token
from say.config import configs
from say.constants import SAY_USER
from say.models import Child
from say.models import City
from say.models import Country
from say.models import EmailVerification
from say.models import Family
from say.models import Need
from say.models import NeedFamily
from say.models import NeedStatusUpdate
from say.models import Ngo
from say.models import Payment
from say.models import PhoneVerification
from say.models import Privilege
from say.models import Receipt
from say.models import ResetPassword
from say.models import SocialWorker
from say.models import State
from say.models import User
from say.models import UserFamily
from say.models.cart import Cart
from say.models.cart import CartNeed
from say.models.receipt import NeedReceipt
from say.roles import SUPER_ADMIN
from say.utils import random_string


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

        # # Disable Sentry
        # import sentry_sdk

        # sentry_sdk.init()

        # get client
        self._client = client

    @staticmethod
    def _mocked_idpay_new_tx(**kwargs):
        return {
            'id': 'daf912385d155c0c414f199e67d025e9',
            'link': 'https://idpay.ir/p/ws-sandbox/abcd',
        }

    @staticmethod
    def _mocked_idpay_new_tx_error(**kwargs):
        return {
            'error_code': list(idpay.ERRORS.keys())[0],
        }

    @property
    def client(self):
        return self._client

    def mockup(self):
        # Override this method to add mockup data
        pass

    @classmethod
    def assert_code(cls, res, code):
        assert res.status_code == code, res.json

    @classmethod
    def assert_ok(cls, res):
        cls.assert_code(res, 200)

    def create_test_file(self, name, size=1000):
        return (io.BytesIO(b"a" * size), name)

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
        seed = randint(10**10, 10**12)
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
                    avatarUrl=self.create_test_file('test.png'),
                    city_id=self._create_city().id,
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
        seed = randint(1, 10**3)
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
            created_by_id=child.id_social_worker,
            isReported=True,
        )
        data.update(kwargs)
        need = Need(**data)
        self.session.save(need)
        return need

    def _create_random_need_status_update(self, need=None, sw=None, **kwargs):
        need = need or self._create_random_need()
        sw = sw or self._create_random_sw(role=SUPER_ADMIN)
        data = dict(
            need=need,
            sw=sw,
            new_status=1,
            old_status=0,
        )
        data.update(kwargs)
        need_status_update = NeedStatusUpdate(**data)
        self.session.save(need_status_update)
        return need_status_update

    def _create_random_receipt(self, owner=None, **kwargs):
        owner = owner or self._create_random_sw()

        seed = randint(1, 10**3)
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

    def _create_random_child(self, sw=None, **kwargs):
        seed = randint(1, 10**3)
        randomstr = str(seed)
        sw = sw or self._create_random_sw()
        data = dict(
            ngo=sw.ngo,
            social_worker=sw,
            firstName=randomstr,
            lastName=randomstr,
            sayName=randomstr,
            phoneNumber=randomstr,
            city=self._create_city(),
            awakeAvatarUrl=randomstr,
            sleptAvatarUrl=randomstr,
            gender=False,
            bio=randomstr,
            bioSummary=randomstr,
            birthDate=datetime.utcnow(),
            nationality=self._create_country(),
            birth_place=self._create_city(),
            voiceUrl=randomstr,
            generatedCode=sw.generated_code + randomstr,
            isConfirmed=choice([True, False]),
            family=Family(),
        )
        data.update(kwargs)
        child = Child(**data)
        self.session.save(child)
        return child

    def _create_random_sw(self, role=SUPER_ADMIN, ngo=None, city=None, **kwargs):
        seed = randint(10**6, 10**9)
        ngo = ngo or self._create_random_ngo()
        city = city or self._create_city()

        data = dict(
            ngo=ngo,
            generated_code=str(seed),
            first_name=str(seed),
            last_name=str(seed),
            username=str(seed),
            id_number=str(seed),
            gender=False,
            telegram_id=str(seed),
            avatar_url=self.create_test_file('test.png'),
            email=f'{str(seed)}@email.com',
            phone_number=f'+98{seed}',
            emergency_phone_number=f'+98{seed}',
            password='abcefg123',
            last_login_date=datetime.utcnow(),
            privilege=Privilege(name=role, privilege=1),
            city=city,
        )

        data.update(kwargs)
        sw = SocialWorker(**data)
        self.session.save(sw)
        return sw

    def _create_random_ngo(self):
        seed = randint(1, 10**3)
        ngo = Ngo(
            _city=self._create_city(),
            name=str(seed),
            emailAddress=f'{str(seed)}@email.com',
            phoneNumber=str(seed),
            logoUrl='',
            postalAddress=str(seed),
            registerDate=datetime.utcnow(),
            isDeleted=False,
        )
        self.session.save(ngo)
        return ngo

    def _create_phone_verification(self, **kwargs):
        seed = randint(1, 10**3)
        data = dict(
            phone_number=f'+9899{seed}',
        )
        data.update(kwargs)
        phone_verification = PhoneVerification(**data)
        self.session.save(phone_verification)
        return phone_verification

    def _create_email_verification(self, **kwargs):
        seed = randint(1, 10**3)
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

        need_family = self._create_need_family(
            need=need,
            user=user,
            family=need.child.family,
        )
        self.session.save(need_family)
        return payment

    def _create_need_family(self, need=None, family=None, user=None, **kwargs):
        need = need or self._create_random_need()
        user = user or self._create_random_user()
        family = family or self._create_random_family()

        data = dict(
            need=need,
            user=user,
            family=family,
            type='app',
        )
        data.update(kwargs)
        need_family = NeedFamily(**data)
        self.session.save(need_family)
        return need_family

    def _create_reset_pass(self, user=None, **kwargs):
        user = user or self._create_random_user()
        data = dict(
            user=user,
            is_used=False,
        )
        data.update(kwargs)
        reset_pass = ResetPassword(**data)
        self.session.save(reset_pass)
        return reset_pass

    def _create_country(self, **kwargs):
        data = dict(
            name=random_string(100),
            iso3=random_string(3),
            numeric_code=random_string(3),
            iso2=random_string(2),
            phone_code=random_string(255),
            capital=random_string(255),
            currency=random_string(255),
            currency_name=random_string(255),
            currency_symbol=random_string(255),
            tld=random_string(255),
            native=random_string(255),
            region=random_string(255),
            subregion=random_string(255),
            timezones=random_string(1),
            translations=random_string(1),
            latitude='1',
            longitude='1',
            emoji=random_string(191),
            emojiU=random_string(191),
            flag=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        data.update(kwargs)
        country = Country(**data)
        self.session.save(country)
        return country

    def _create_state(self, country=None, **kwargs):
        country = country or self._create_country()

        data = dict(
            name='Tehran',
            country_code='IR',
            country_name='Iran',
            state_code='IR',
            fips_code=26,
            iso2=23,
            latitude="35.72484160",
            longitude="51.38165300",
            type='province',
            flag=1,
            country=country,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        data.update(kwargs)
        state = State(**data)
        self.session.save(state)
        return state

    def _create_city(self, country=None, state=None, **kwargs):
        country = country or self._create_country()
        state = state or self._create_state(country=country)

        data = dict(
            name='Tehran',
            state_code='23',
            state_name='asd',
            country_code='IR',
            country_name='Iran',
            latitude="35.72484160",
            longitude="51.38165300",
            state=state,
            country=country,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        data.update(kwargs)
        city = City(**data)
        self.session.save(city)
        return city

    def _create_say_user(self):
        return self._create_random_user(userName=SAY_USER)

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
