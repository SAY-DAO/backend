from datetime import datetime
from khayyam import JalaliDate
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import object_session
from flask import render_template
from say.utils import get_price
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

    @hybrid_property
    def cost(self):
        if not self.link or self.isDone:
            return self._cost
        return get_price(self.link)

    @cost.expression
    def cost(cls):
        return

    @hybrid_property
    def progress(self):
        try:
           if not self.link or self.isDone:
               return int(self.paid / self._cost * 100)

           return int(self.paid / self.cost * 100)
        except:
            return 0

    @progress.expression
    def progress(cls):
        return

    child = relationship('ChildModel', foreign_keys=child_id, uselist=False)
    need_family = relationship(
        'NeedFamilyModel',
        uselist=False,
        back_populates='need',
    )

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

