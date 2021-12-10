import string
from datetime import datetime
from datetime import timedelta

from argon2 import PasswordHasher
from babel import Locale
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import synonym
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.sqltypes import Text
from sqlalchemy_utils import LocaleType
from sqlalchemy_utils.models import Timestamp

from say.formatters import expose_datetime
from say.locale import ChangeLocaleTo
from say.locale import get_locale
from say.orm import base
from say.orm.mixins import ActivateMixin
from say.orm.types import LocalFile
from say.render_template_i18n import render_template_i18n
from say.utils import surname
from say.validations import validate_password as _validate_password


"""
SocialWorker Model
"""

PASSOWRD_LENGTH = 12
PASSOWRD_LETTERS = string.ascii_letters + string.digits


# TODO: unique email, phone, username, ...
class SocialWorker(base, Timestamp, ActivateMixin):
    __tablename__ = "social_worker"

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    generatedCode = Column(String, nullable=False)

    id_ngo = Column(Integer, ForeignKey('ngo.id'), nullable=False, index=True)
    id_type = Column(
        Integer, ForeignKey('social_worker_type.id'), nullable=False, index=True
    )

    country = Column(Integer, nullable=True)
    city = Column(Integer, nullable=True)
    firstName = Column(String, nullable=True)
    lastName = Column(String, nullable=False)
    userName = Column(
        String, nullable=False, unique=True
    )  # ngoName + "-sw" + generatedCode
    _password = Column(String(256), nullable=False)
    birthCertificateNumber = Column(String, nullable=True)
    idNumber = Column(String, nullable=False)
    idCardUrl = Column(
        LocalFile(dst='social-workers/id-cards', filename_length=64),
        nullable=True,
        unique=True,
    )
    passportNumber = Column(String, nullable=True)
    passportUrl = Column(
        LocalFile(dst='social-workers/passports', filename_length=64),
        nullable=True,
        unique=True,
    )
    gender = Column(Boolean, nullable=False)
    birthDate = Column(Date, nullable=True)
    phoneNumber = Column(String, nullable=False, unique=True)
    emergencyPhoneNumber = Column(String, nullable=False)
    emailAddress = Column(String, nullable=False, unique=True)
    telegramId = Column(String, nullable=False)
    postalAddress = Column(Text, nullable=True)
    avatarUrl = Column(
        LocalFile(dst='social-workers/avatars', filename_length=64),
        unique=True,
        nullable=False,
    )
    childCount = Column(Integer, nullable=False, default=0)
    currentChildCount = Column(Integer, nullable=False, default=0)
    needCount = Column(Integer, nullable=False, default=0)
    currentNeedCount = Column(Integer, nullable=False, default=0)
    bankAccountNumber = Column(String, nullable=True)
    bankAccountShebaNumber = Column(String, nullable=True)
    bankAccountCardNumber = Column(String, nullable=True)
    lastLoginDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    lastLogoutDate = Column(DateTime, nullable=True)
    # isActive = Column(Boolean, nullable=False, default=True)
    isDeleted = Column(Boolean, nullable=False, default=False, index=True)
    locale = Column(LocaleType, default=Locale('fa'), nullable=False)

    privilege = relationship("Privilege", foreign_keys=[id_type], lazy='selectin')
    ngo = relationship("Ngo", foreign_keys=id_ngo)
    children = relationship("Child", back_populates='social_worker')

    typeName = association_proxy('privilege', 'name')
    ngoName = association_proxy('ngo', 'name')

    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        if not _validate_password(password):
            raise ValueError('Password must be at least 6 character')

        ph = PasswordHasher()
        self._password = ph.hash(password)

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym(
        '_password',
        descriptor=property(_get_password, _set_password),
        info=dict(protected=True),
    )

    def validate_password(self, password):
        ph = PasswordHasher()
        return ph.verify(self.password, password)

    def send_password(self, password):
        from say.authorization import create_sw_access_token
        from say.tasks import send_embeded_subject_email

        send_embeded_subject_email.delay(
            to=self.emailAddress,
            html=render_template_i18n(
                'social_worker_password.html',
                social_worker=self,
                surname=surname(self.gender),
                password=password,
                token=create_sw_access_token(self),
                locale=self.locale,
            ),
        )

    @staticmethod
    def generate_password():
        from say.utils import random_string

        return random_string(
            length=PASSOWRD_LENGTH,
            letters=PASSOWRD_LETTERS,
        )

    def send_report(self):
        from say.app import app
        from say.orm import safe_commit
        from say.tasks import send_embeded_subject_email

        from .child_model import Child
        from .child_need_model import ChildNeed
        from .need_model import Need
        from .ngo_model import Ngo

        session = object_session(self)
        needs = None
        with app.app_context(), ChangeLocaleTo(self.locale):
            needs = (
                session.query(Need)
                .filter(Need.isReported.isnot(True))
                .filter(Need.status == 3)
                .join(ChildNeed)
                .join(Child)
                .filter(Child.id_social_worker == self.id)
                .order_by(
                    Child.firstName,
                    Child.lastName,
                    Need.expected_delivery_date,
                )
            )
            services = []
            products = []
            for need in needs:
                if need.type == 0:
                    services.append(need)
                elif need.type == 1 and need.expected_delivery_date:
                    products.append(need)
                else:
                    continue

            # This date show when the needs status updated to 3
            date = datetime.utcnow() - timedelta(days=1)
            say = session.query(Ngo).filter_by(name='SAY').first()
            bcc = [say.coordinator.emailAddress]
            coordinator_email = self.ngo.coordinator.emailAddress
            locale = self.locale

            if len(services) != 0:
                send_embeded_subject_email.delay(
                    to=self.emailAddress,
                    cc=coordinator_email,
                    bcc=bcc,
                    html=render_template_i18n(
                        'social_worker_report_service.html',
                        needs=services,
                        social_worker=self,
                        surname=surname(self.gender),
                        date=date,
                        locale=locale,
                    ),
                )

                for need in services:
                    need.isReported = True

                safe_commit(session)

            if len(products) != 0:
                use_plural = False if len(products) == 1 else True
                send_embeded_subject_email.delay(
                    to=self.emailAddress,
                    cc=coordinator_email,
                    bcc=bcc,
                    html=render_template_i18n(
                        'social_worker_report_product.html',
                        needs=products,
                        social_worker=self,
                        surname=surname(self.gender),
                        date=date,
                        use_plural=use_plural,
                        date_formater=lambda dt: expose_datetime(dt, locale=get_locale()),
                        locale=locale,
                    ),
                )

                for need in products:
                    need.isReported = True

                safe_commit(session)

            return [need.id for need in needs]
