from datetime import datetime, timedelta
from khayyam import JalaliDate
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import object_session
from flask import render_template
from say.tasks import send_email
from . import *

"""
Need Model
"""


class NeedModel(base):
    __tablename__ = "need"

    id = Column(Integer, nullable=False, primary_key=True, unique=True)

    child_id = Column(Integer, ForeignKey('child.id'))

    name = Column(String, nullable=False)
    imageUrl = Column(String, nullable=False)
    category = Column(Integer, nullable=False)  # 0:Growth | 1:Joy | 2:Health | 3:Surroundings
    isUrgent = Column(Boolean, nullable=False)
    description = Column(Text, nullable=False)
    descriptionSummary = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    _cost = Column(Integer, nullable=False)
    paid = Column(Integer, nullable=False, default=0)
    donated = Column(Integer, nullable=False, default=0)
    link = Column(String, nullable=True)
    affiliateLinkUrl = Column(String, nullable=True)
    isDone = Column(Boolean, nullable=False, default=False)
    doneAt = Column(DateTime, nullable=True)
    isDeleted = Column(Boolean, nullable=False, default=False)
    createdAt = Column(DateTime, nullable=False)
    receipts = Column(String, nullable=True)  # comma separated
    isConfirmed = Column(Boolean, nullable=False, default=False)
    confirmDate = Column(DateTime, nullable=True)
    confirmUser = Column(Integer, nullable=True)
    type = Column(Integer, nullable=False)  # 0:service | 1:product
    lastUpdate = Column(DateTime, nullable=False)
    doing_duration = Column(Integer, nullable=False, default=5)
    status = Column(Integer, nullable=False, default=0)
    isReported = Column(Boolean, default=False)
    delivery_date = Column(Date)
    img = Column(Text, nullable=True)
    title = Column(Text, nullable=True)

    def _set_cost(self, cost):
        self._cost = cost

    def _get_cost(self):
        return self._cost

    cost = synonym(
        '_cost',
        descriptor=property(_get_cost, _set_cost),
    )

    @hybrid_property
    def progress(self):
        try:
           return int(self.paid / self.cost * 100)
        except:
            return 0

    @progress.expression
    def progress(cls):
        return

    child = relationship('ChildModel', foreign_keys=child_id, uselist=False)
    payments = relationship('PaymentModel', back_populates='need')
    need_family = relationship(
        'NeedFamilyModel',
        uselist=False,
        back_populates='need',
    )

    def update(self):
        from say.utils import digikala
        data = digikala.get_data(self.link)
        cost = data['cost']
        if cost:
            self.cost = data['cost']

        img = data['img']
        if img:
            self.img = data['img']

        title = data['title']
        if title:
            self.title = data['title']

        return data

    def send_purchase_email(self):
        session = object_session(self)
        cc_emails = {user.emailAddress for user in self.child.families[0].users}
        participants = participants = (
                session.query(self.need_family.__class__)
                .filter_by(id_need=self.id)
                .filter_by(isDeleted=False)
            )

        to_emails = set()
        for participate in participants:
            to_emails.add(participate.user.emailAddress)

        cc_emails -= to_emails
        iran_date = JalaliDate(datetime.utcnow()).localdateformat()
        send_email.delay(
            subject=f'رسید خرید کالای {self.child.sayName} توسط SAY',
            emails=list(to_emails),
            cc=list(cc_emails),
            html=render_template(
                'status_purchased.html',
                 child=self.child,
                 need=self,
                 date=iran_date,
            ),
         )

    def send_child_delivery_product_email(self):
        session = object_session(self)
        cc_emails = {user.emailAddress for user in self.child.families[0].users}
        participants = participants = (
                session.query(self.need_family.__class__)
                .filter_by(id_need=self.id)
                .filter_by(isDeleted=False)
            )

        to_emails = set()
        for participate in participants:
            to_emails.add(participate.user.emailAddress)

        cc_emails -= to_emails
        iran_date = JalaliDate(datetime.utcnow()).localdateformat()
        send_email.apply_async((
               f'اطلاع از رسیدن کالا به {self.child.sayName}',
               list(to_emails),
               render_template(
                   'status_child_delivery_product.html',
                    child=self.child,
                    need=self,
                    date=iran_date,
               ),
               list(cc_emails),
            ),
            eta=datetime.utcnow() + timedelta(minutes=5),
        )
        #  TODO: change status to 5

    def send_child_delivery_service_email(self):
        session = object_session(self)
        cc_emails = {user.emailAddress for user in self.child.families[0].users}
        participants = participants = (
                session.query(self.need_family.__class__)
                .filter_by(id_need=self.id)
                .filter_by(isDeleted=False)
            )

        to_emails = set()
        for participate in participants:
            to_emails.add(participate.user.emailAddress)

        cc_emails -= to_emails
        iran_date = JalaliDate(datetime.utcnow()).localdateformat()
        send_email.delay(
            subject=f'{self.name} به دست {self.child.sayName} رسید',
            emails=list(to_emails),
            cc=list(cc_emails),
            html=render_template(
                'status_child_delivery_service.html',
                 child=self.child,
                 need=self,
                 date=iran_date,
            ),
         )


    def send_money_to_ngo_email(self):
        session = object_session(self)
        cc_emails = {user.emailAddress for user in self.child.families[0].users}
        participants = participants = (
                session.query(self.need_family.__class__)
                .filter_by(id_need=self.id)
                .filter_by(isDeleted=False)
            )

        to_emails = set()
        for participate in participants:
            to_emails.add(participate.user.emailAddress)

        cc_emails -= to_emails
        iran_date = JalaliDate(datetime.utcnow()).localdateformat()
        send_email.delay(
            subject=f'رسید انتقال وجه به انجمن توسط SAY',
            emails=list(to_emails),
            cc=list(cc_emails),
            html=render_template(
                'status_money_to_ngo.html',
                 need=self,
                 child=self.child,
                 date=iran_date,
            ),
        )

