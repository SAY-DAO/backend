from sqlalchemy.orm import object_session

from say.api import render_template, expose_datetime
from say.tasks import send_email, send_embeded_subject_email
from say.utils import surname
from . import *

"""
NGO Model
"""


class Ngo(base, Timestamp):
    __tablename__ = "ngo"

    id = Column(Integer, primary_key=True, nullable=False, unique=True)

    coordinatorId = Column(Integer, ForeignKey('social_worker.id'), nullable=False)

    country = Column(Integer, nullable=False)
    city = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    postalAddress = Column(Text, nullable=False)
    emailAddress = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=False)
    website = Column(String, nullable=True)
    logoUrl = Column(String, nullable=False)
    balance = Column(Integer, nullable=False, default=0)
    socialWorkerCount = Column(Integer, nullable=False, default=0)
    currentSocialWorkerCount = Column(Integer, nullable=False, default=0)
    childrenCount = Column(Integer, nullable=False, default=0)
    currentChildrenCount = Column(Integer, nullable=False, default=0)
    registerDate = Column(DateTime, nullable=False)
    isActive = Column(Boolean, nullable=False, default=True)
    isDeleted = Column(Boolean, nullable=False, default=False)

    coordinator = relationship(
        'SocialWorker',
        foreign_keys=coordinatorId,
        uselist=False,
    )

    def send_report_to_ngo(self):
        session = object_session(self)
        from .need_model import Need
        from .child_model import Child
        from .child_need_model import ChildNeed

        needs = session.query(Need) \
            .filter(Need.isReported != True) \
            .filter(Need.status == 3) \
            .join(ChildNeed) \
            .join(Child) \
            .filter(Child.id_ngo==self.id)

        services = []
        products = []
        for need in needs:
            if need.type == 0:
                services.append(need)
            elif need.type == 1 and need.expected_delivery_date:
                products.append(need)
            else:
                continue

        from say.api import app

        # This date show when the needs status updated to 3
        date = datetime.utcnow() - timedelta(days=1)
        say = session.query(Ngo).filter_by(name='SAY').first()
        bcc = [say.coordinator.emailAddress]
        coordinator_email = self.coordinator.emailAddress
        locale = self.coordinator.locale

        with app.app_context():
            if len(services) != 0:
                send_embeded_subject_email.delay(
                    to=coordinator_email,
                    bcc=bcc,
                    html=render_template(
                        'ngo_report_service.html',
                        needs=services,
                        ngo=self,
                        surname=surname(self.coordinator.gender),
                        date=date,
                        locale=locale,
                    ),
                 )

                for need in services:
                    need.isReported = True

            if len(products) != 0:
                use_plural = False if len(products) == 1 else True
                send_embeded_subject_email.delay(
                    to=coordinator_email,
                    bcc=bcc,
                    html=render_template(
                        'ngo_report_product.html',
                        needs=products,
                        ngo=self,
                        surname=surname(self.coordinator.gender),
                        date=date,
                        use_plural=use_plural,
                        date_formater=
                            lambda dt: expose_datetime(dt, locale=get_locale()),
                        locale=locale,
                    ),
                 )

                for need in products:
                    need.isReported = True

        session.commit()
        return [need.id for need in needs]

