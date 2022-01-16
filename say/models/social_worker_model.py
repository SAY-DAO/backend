import string
from datetime import datetime
from datetime import timedelta

from argon2 import PasswordHasher
from babel import Locale
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import column_property
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import synonym
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.functions import func
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
from say.models import Child
from say.models import Need
from say.orm import base
from say.orm.mixins import ActivateMixin
from say.orm.mixins import SoftDeleteMixin
from say.orm.types import LocalFile
from say.render_template_i18n import render_template_i18n
from say.utils import surname
from say.validations import validate_password as _validate_password

from .base_user import BaseUser


"""
SocialWorker Model
"""

PASSOWRD_LENGTH = 12
PASSOWRD_LETTERS = string.ascii_letters + string.digits


# TODO: unique email, phone, username, ...
class SocialWorker(BaseUser, Timestamp, ActivateMixin, SoftDeleteMixin):
    __tablename__ = "social_worker"
    __versioned__ = {}
    __mapper_args__ = {
        'polymorphic_identity': 'social_worker',
    }

    id = Column(
        Integer,
        ForeignKey('base_users.id'),
        primary_key=True,
        nullable=False,
        unique=True,
    )
    generated_code = Column(String, nullable=False)

    ngo_id = Column(Integer, ForeignKey('ngo.id'), nullable=False, index=True)
    type_id = Column(
        Integer, ForeignKey('social_worker_type.id'), nullable=False, index=True
    )

    is_coordinator = Column(Boolean, default=False, nullable=False)

    country = Column(Integer, nullable=True)
    city = Column(Integer, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    username = Column(
        String, nullable=False, unique=True
    )  # ngoName + "-sw" + generatedCode
    _password = Column(String(256), nullable=False)
    birth_certificate_number = Column(String, nullable=True)
    id_number = Column(String, nullable=False)
    id_card_url = Column(
        LocalFile(dst='social-workers/id-cards', filename_length=64),
        nullable=True,
        unique=True,
    )
    passport_number = Column(String, nullable=True)
    passport_url = Column(
        LocalFile(dst='social-workers/passports', filename_length=64),
        nullable=True,
        unique=True,
    )
    gender = Column(Boolean, nullable=False)
    birth_date = Column(Date, nullable=True)
    phone_number = Column(String, nullable=False, unique=True)
    emergency_phone_number = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    telegram_id = Column(String, nullable=False)
    postal_address = Column(Text, nullable=True)
    avatar_url = Column(
        LocalFile(dst='social-workers/avatars', filename_length=64),
        unique=True,
        nullable=False,
    )
    # childCount = Column(Integer, nullable=False, default=0)
    # currentChildCount = Column(Integer, nullable=False, default=0)
    # need_count = Column(Integer, nullable=False, default=0)
    # current_need_count = Column(Integer, nullable=False, default=0)
    bank_account_number = Column(String, nullable=True)
    bank_account_sheba_number = Column(String, nullable=True)
    bank_account_card_number = Column(String, nullable=True)
    last_login_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    # lastLogoutDate = Column(DateTime, nullable=True)
    # isActive = Column(Boolean, nullable=False, default=True)
    # is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    locale = Column(LocaleType, default=Locale('fa'), nullable=False)

    privilege = relationship("Privilege", foreign_keys=[type_id], lazy='selectin')
    ngo = relationship("Ngo", foreign_keys=ngo_id)
    children = relationship("Child", back_populates='social_worker')

    type_name = association_proxy('privilege', 'name')
    ngo_name = association_proxy('ngo', 'name')

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

    child_count = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            and_(
                Child.id_social_worker == id,
            )
        )
    )

    current_child_count = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            and_(
                Child.id_social_worker == id,
                Child.isDeleted.is_(False),
                Child.isMigrated.is_(False),
            )
        )
    )

    need_count = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            and_(
                Child.id_social_worker == id,
                Need.child_id == Child.id,
            )
        )
    )

    current_need_count = column_property(
        select([coalesce(func.count(1), 0,)]).where(
            and_(
                Child.id_social_worker == id,
                Need.child_id == Child.id,
                Need.isDeleted.is_(False),
                Need.isConfirmed.is_(True),
            )
        )
    )

    def validate_password(self, password):
        ph = PasswordHasher()
        return ph.verify(self.password, password)

    def send_password(self, password):
        from say.authorization import create_sw_access_token
        from say.tasks import send_embeded_subject_email

        send_embeded_subject_email.delay(
            to=self.email,
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
            say = session.query(Ngo).filter_by(name='SAY').one()
            bcc = [s.email for s in say.coordinators]
            coordinators_email = [s.email for s in self.ngo.coordinators]
            locale = self.locale

            if len(services) != 0:
                send_embeded_subject_email.delay(
                    to=self.email,
                    cc=coordinators_email,
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
                    to=self.email,
                    cc=coordinators_email,
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

            return {
                'to': self.email,
                'cc': coordinators_email,
                'bcc': bcc,
                'needs': [need.id for need in needs],
            }
