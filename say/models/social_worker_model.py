from babel import Locale
from celery import exceptions
from sqlalchemy.orm import object_session
from sqlalchemy_utils import LocaleType

from say.formatters import expose_datetime
from say.locale import ChangeLocaleTo
from say.render_template_i18n import render_template_i18n
from say.utils import surname

from . import *


"""
SocialWorker Model
"""


class SocialWorker(base, Timestamp):
    __tablename__ = "social_worker"

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    generatedCode = Column(String, nullable=False)

    id_ngo = Column(Integer, ForeignKey('ngo.id'), nullable=False, index=True)
    id_type = Column(Integer, ForeignKey('social_worker_type.id'), nullable=False, index=True)

    country = Column(Integer, nullable=True)
    city = Column(Integer, nullable=True)
    firstName = Column(String, nullable=True)
    lastName = Column(String, nullable=False)
    userName = Column(String, nullable=False)  # ngoName + "-sw" + generatedCode
    password = Column(String, nullable=False)
    birthCertificateNumber = Column(String, nullable=True)
    idNumber = Column(String, nullable=False)
    idCardUrl = Column(String, nullable=True)
    passportNumber = Column(String, nullable=True)
    passportUrl = Column(String, nullable=True)
    gender = Column(Boolean, nullable=False)
    birthDate = Column(Date, nullable=True)
    phoneNumber = Column(String, nullable=False)
    emergencyPhoneNumber = Column(String, nullable=False)
    emailAddress = Column(String, nullable=False)
    telegramId = Column(String, nullable=False)
    postalAddress = Column(Text, nullable=True)
    avatarUrl = Column(String, nullable=False)
    childCount = Column(Integer, nullable=False, default=0)
    currentChildCount = Column(Integer, nullable=False, default=0)
    needCount = Column(Integer, nullable=False, default=0)
    currentNeedCount = Column(Integer, nullable=False, default=0)
    bankAccountNumber = Column(String, nullable=True)
    bankAccountShebaNumber = Column(String, nullable=True)
    bankAccountCardNumber = Column(String, nullable=True)
    registerDate = Column(Date, nullable=False)
    lastLoginDate = Column(Date, nullable=False)
    lastLogoutDate = Column(Date, nullable=True)
    isActive = Column(Boolean, nullable=False, default=True)
    isDeleted = Column(Boolean, nullable=False, default=False, index=True)
    locale = Column(LocaleType, default=Locale('fa'), nullable=False)

    privilege = relationship("Privilege", foreign_keys=id_type)
    ngo = relationship("Ngo", foreign_keys=id_ngo)
    children = relationship("Child", back_populates='social_worker')

    def send_report(self):
        from say.tasks import send_embeded_subject_email
        from .need_model import Need
        from .child_model import Child
        from .child_need_model import ChildNeed
        from .ngo_model import Ngo
        from say.orm import safe_commit
        from say.app import app

        session = object_session(self)
        needs = None
        with app.app_context(), ChangeLocaleTo(self.locale):
            needs = session.query(Need) \
                .filter(Need.isReported != True) \
                .filter(Need.status == 3) \
                .join(ChildNeed) \
                .join(Child) \
                .filter(Child.id_social_worker==self.id) \
                .order_by(
                    Child.firstName,
                    Child.lastName,
                    Need.expected_delivery_date,
                ) \

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
                        date_formater=
                            lambda dt: expose_datetime(dt, locale=get_locale()),
                        locale=locale,
                    ),
                 )

                for need in products:
                    need.isReported = True

                safe_commit(session)

            return [need.id for need in needs]
