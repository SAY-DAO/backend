from sqlalchemy.orm import object_session
from flask import render_template

from say.tasks import send_email
from say.utils import surname
from . import *

"""
NGO Model
"""


class NgoModel(base):
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
    lastUpdateDate = Column(DateTime, nullable=False)
    isActive = Column(Boolean, nullable=False, default=True)
    isDeleted = Column(Boolean, nullable=False, default=False)

    coordinator = relationship(
        'SocialWorkerModel',
        foreign_keys=coordinatorId,
        uselist=False,
    )

    def send_report_to_ngo(self):
        session = object_session(self)
        from .need_model import NeedModel
        from .child_model import ChildModel
        from .child_need_model import ChildNeedModel

        needs = session.query(NeedModel) \
            .filter(NeedModel.isReported != True) \
            .filter(NeedModel.status == 3) \
            .join(ChildNeedModel) \
            .join(ChildModel) \
            .filter(ChildModel.id_ngo==self.id)

        services = []
        products = []
        for need in needs:
            if need.type == 0: # service
                services.append(need)
            elif need.type == 1: # product
                products.append(need)
            else:
                continue

        from say.api import app

        # This date show when the needs status updated to 3
        date = JalaliDate(datetime.utcnow() - timedelta(days=1))
        formated_date = format_jalali_date(date)
        say = session.query(NgoModel).filter_by(name='SAY').first()
        bcc = [say.coordinator.emailAddress]

        if len(services) != 0:
            with app.app_context():
                send_email.delay(
                    subject='اطلاع از واریز وجه توسط SAY',
                    emails=self.coordinator.emailAddress,
                    bcc=bcc,
                    html=render_template(
                        'ngo_report_service.html',
                        needs=services,
                        ngo=self,
                        surname=surname(self.coordinator.gender),
                        date=formated_date,
                    ),
                 )

        if len(products) != 0:
            for need in products:
                if need.expected_delivery_date:
                    date = JalaliDate(need.expected_delivery_date)
                    need.delivere_at = format_jalali_date(date)
                else:
                    need_delivere_at = None

            with app.app_context():
                send_email.delay(
                    subject='اطلاع‌رسانی خرید کالا توسط SAY',
                    emails=self.coordinator.emailAddress,
                    bcc=bcc,
                    html=render_template(
                        'ngo_report_product.html',
                        needs=products,
                        ngo=self,
                        surname=surname(self.coordinator.gender),
                        date=formated_date,
                        miladi_to_jalali=JalaliDate
                    ),
                 )

        for need in needs:
            need.isReported = True

        session.commit()
        return [need.id for need in needs]

