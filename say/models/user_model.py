import os
from hashlib import sha256

from . import *


"""
User Model
"""


class UserModel(base):
    __tablename__ = "user"

    id = Column(Integer, nullable=False, primary_key=True, unique=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    userName = Column(String, nullable=False, unique=True)
    credit = Column(Integer, nullable=False, default=0)
    avatarUrl = Column(String, nullable=True)
    flagUrl = Column(String, nullable=True)
    phoneNumber = Column(String, nullable=True)
    emailAddress = Column(String, nullable=True, unique=True)
    gender = Column(Boolean, nullable=True)  # real country codes
    city = Column(Integer, nullable=False)  # 1:tehran | 2:karaj
    country = Column(Integer, nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)
    isVerified = Column(Boolean, nullable=False, default=False)
    createdAt = Column(Date, nullable=False)
    lastUpdate = Column(Date, nullable=False)
    birthDate = Column(Date, nullable=True)
    birthPlace = Column(Integer, nullable=True)  # 1:tehran | 2:karaj
    lastLogin = Column(Date, nullable=False)
    _password = Column(String, nullable=False)
    spentCredit = Column(Integer, nullable=False, default=0)
    doneNeedCount = Column(Integer, nullable=False, default=0)

    #payments = relationship('PaymentModel', back_populates='user')
    # families = relationship(
    #     'FamilyModel',
    #     secondary='user_family',
    #     back_populates='users',
    # )

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

