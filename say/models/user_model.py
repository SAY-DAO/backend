import os
import enum
from hashlib import sha256

from sqlalchemy.orm import composite
from sqlalchemy_utils import LocaleType, CountryType, PhoneNumberType
from babel import Locale

from say.validations import validate_password as _validate_password
from say.gender import Gender
from . import *


"""
User Model
"""


class User(base, Timestamp):
    __tablename__ = "user"

    id = Column(Integer, nullable=False, primary_key=True, unique=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    userName = Column(String, nullable=False, unique=True)
    avatarUrl = Column(String, nullable=True)
    flagUrl = Column(String, nullable=True)
    phone_number = Column(PhoneNumberType(), unique=True, index=True)
    country = Column(CountryType, nullable=False)
    emailAddress = Column(String, nullable=True, unique=True, index=True)
    gender = Column(Enum(Gender), nullable=True)
    city = Column(Integer, nullable=False)  # 1:tehran | 2:karaj
    isDeleted = Column(Boolean, nullable=False, default=False)
    is_email_verified = Column(Boolean, nullable=False, default=False)
    is_phonenumber_verified = Column(Boolean, nullable=False, default=False)
    birthDate = Column(Date, nullable=True)
    birthPlace = Column(Integer, nullable=True)  # 1:tehran | 2:karaj
    lastLogin = Column(DateTime, nullable=False)
    _password = Column(String, nullable=False)
    locale = Column(LocaleType, default=Locale('fa'), nullable=False)

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

    @aggregated('participations.need', Column(Integer, default=0, nullable=False))
    def done_needs_count(cls):
        from . import Need
        # passing a dummy '1' to count
        return func.count('1') \
            .filter(Need.status > 1)

    @aggregated('payments', Column(Integer, default=0, nullable=False))
    def spent(cls):
        from . import Payment
        return coalesce(
            func.sum(Payment.need_amount),
            0,
        )

    @aggregated('payments', Column(Integer, default=0, nullable=False))
    def credit(cls):
        from . import Payment
        return coalesce(
            func.sum(-Payment.credit_amount),
            0,
        )

    payments = relationship(
        'Payment',
        back_populates='user',
        primaryjoin=
            'and_(User.id==Payment.id_user, Payment.verified.isnot(None))',
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

    def _hash_password(cls, password):
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
        info=dict(protected=True)
    )

    def validate_password(self, password):
        hashed_pass = sha256()
        hashed_pass.update((password + self.password[:64]).encode('utf-8'))
        return self.password[64:] == hashed_pass.hexdigest()

    def charge(self, amount):
        from . import Payment
        session = object_session(self)

        payment = Payment(
            credit_amount=-amount,
            use_credit=True,
        )
        payment.verify()
        self.payments.append(payment)
        session.add(payment)

