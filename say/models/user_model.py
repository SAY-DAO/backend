from hashlib import sha256
from os.path import join

from sqlalchemy.orm import column_property
from sqlalchemy_utils import CountryType
from sqlalchemy_utils import LocaleType
from sqlalchemy_utils import PhoneNumberType

from say.config import configs
from say.content import content
from say.gender import Gender
from say.locale import ChangeLocaleTo
from say.orm.types import LocalFile
from say.orm.types import ResourceURL
from say.render_template_i18n import render_template_i18n
from say.validations import validate_password as _validate_password

from . import *
from .base_user import BaseUser
from .need_model import Need
from .need_model import NeedFamily
from .payment_model import Payment


"""
User Model
"""


class User(BaseUser, Timestamp):
    __tablename__ = 'user'
    __versioned__ = {}

    __mapper_args__ = {
        'polymorphic_identity': 'user',
    }

    id = Column(
        Integer,
        ForeignKey('base_users.id'),
        nullable=False,
        primary_key=True,
        unique=True,
    )

    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    userName = Column(String, nullable=False, unique=True)
    avatarUrl = Column(
        LocalFile(dst='users/avatars'),
        nullable=True,
        unique=True,
    )
    phone_number = Column(PhoneNumberType(), unique=True, index=True, nullable=True)
    country = Column(CountryType, nullable=True)
    city = Column(Integer, nullable=False)  # 1:tehran | 2:karaj
    postal_address = Column(Text, nullable=True)
    postal_code = Column(Unicode(10), nullable=True)
    emailAddress = Column(String, nullable=True, unique=True, index=True)
    gender = Column(Enum(Gender), nullable=True)
    isDeleted = Column(Boolean, nullable=False, default=False)
    is_email_verified = Column(Boolean, nullable=False, default=False, index=True)
    is_phonenumber_verified = Column(Boolean, nullable=False, default=False, index=True)
    birthDate = Column(Date, nullable=True)
    birthPlace = Column(Integer, nullable=True)  # 1:tehran | 2:karaj
    lastLogin = Column(DateTime, nullable=False)
    _password = Column(String, nullable=False)
    locale = Column(LocaleType, default=Locale('fa'), nullable=False)
    is_installed = Column(Boolean, default=False, nullable=False)
    is_nakama = Column(Boolean, default=False, nullable=False, index=True)
    receive_email = Column(Boolean, default=True, nullable=False)
    receiveEmail = synonym('receive_email')

    @hybrid_property
    def formated_username(self):
        return self.userName.lower()

    @formated_username.expression
    def formated_username(cls):
        return func.lower(cls.userName)

    @hybrid_property
    def isVerified(self):
        return self.is_phonenumber_verified or self.is_email_verified

    @isVerified.expression
    def isVerified(cls):
        return or_(cls.is_phonenumber_verified, cls.is_email_verified)

    spent = column_property(
        select([coalesce(func.sum(Payment.need_amount), 0,)]).where(
            and_(
                Payment.verified.isnot(None),
                Payment.id_user == id,
            )
        )
    )

    credit = column_property(
        select([coalesce(func.sum(-Payment.credit_amount), 0,)]).where(
            and_(
                Payment.verified.isnot(None),
                Payment.id_user == id,
            )
        )
    )

    done_needs_count = column_property(
        select([coalesce(func.count(Need.id), 0,)]).where(
            and_(
                NeedFamily.id_user == id,
                NeedFamily.id_need == Need.id,
                Need.status >= 2,
                Need.isDeleted.is_(False),
            )
        )
    )

    payments = relationship(
        'Payment',
        back_populates='user',
        primaryjoin='and_(User.id==Payment.id_user, Payment.verified.isnot(None))',
    )
    user_families = relationship(
        'UserFamily',
        back_populates='user',
        primaryjoin='and_(UserFamily.id_user==User.id, ~UserFamily.isDeleted)',
    )
    participations = relationship(
        'NeedFamily',
        back_populates='user',
    )
    sent_invitations = relationship(
        'Invitation',
        back_populates='inviter',
    )

    invitation_accepts = relationship(
        'InvitationAccept',
        back_populates='invitee',
    )

    cart = relationship(
        'Cart',
        uselist=False,
        back_populates='user',
    )

    def _hash_password(self, password):
        password = str(password)
        salt = sha256()
        salt.update(os.urandom(60))
        salt = salt.hexdigest()

        hashed_pass = sha256()
        # Make sure password is a str because we cannot hash unicode objects
        hashed_pass.update((password + salt).encode('utf-8'))
        hashed_pass = hashed_pass.hexdigest()

        password = salt + hashed_pass
        return password

    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        if not _validate_password(password):
            raise ValueError('Password must be at least 6 character')

        self._password = self._hash_password(password)

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym(
        '_password',
        descriptor=property(_get_password, _set_password),
        info=dict(protected=True),
    )

    def validate_password(self, password):
        hashed_pass = sha256()
        hashed_pass.update((password + self.password[:64]).encode('utf-8'))
        return self.password[64:] == hashed_pass.hexdigest()

    def charge_wallet(self, amount):
        from . import Payment

        session = object_session(self)

        payment = Payment(
            credit_amount=-amount,
            user=self,
        )
        session.add(payment)
        payment.verify()
        self.payments.append(payment)
        session.add(payment)

    def create_cart(self):
        from say.models import Cart

        self.cart = Cart(user=self)

    def send_installion_notif(self, notif_url):
        from say.tasks import send_embeded_subject_email
        from say.tasks import send_sms

        with ChangeLocaleTo(self.locale):
            if self.is_phonenumber_verified:
                send_sms.delay(
                    self.phone_number.e164,
                    content['INSTALLION'] % notif_url,
                )

            elif self.is_email_verified:
                send_embeded_subject_email.delay(
                    to=self.emailAddress,
                    html=render_template_i18n(
                        'installion.html',
                        locale=self.locale,
                        link=notif_url,
                    ),
                )
            else:
                raise Exception('User has not a verified contact, BUG!')
