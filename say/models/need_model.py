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
    oncePurchased = Column(Boolean, nullable=False, default=False)

    def _set_cost(self, cost):
        cost = int(str(cost).replace(',', ''))
        self._cost = cost

    def _get_cost(self):
        return self._cost

    cost = synonym(
        '_cost',
        descriptor=property(_get_cost, _set_cost),
    )

    @hybrid_property
    def progress(self):
        if self.isDone:
            return 100

        try:
           return int(self.paid / self.cost * 100)
        except:
            return 0

    @progress.expression
    def progress(cls):
        return

    child = relationship(
        'ChildModel',
        foreign_keys=child_id,
        uselist=False,
        back_populates='needs',
    )
    payments = relationship('PaymentModel', back_populates='need')
    need_family = relationship(
        'NeedFamilyModel',
        uselist=False,
        back_populates='need',
    )

    @hybrid_property
    def participants(self):
        from .user_model import UserModel
        from .payment_model import PaymentModel

        session = object_session(self)
        participants_query = session.query(
            func.sum(PaymentModel.amount),
            UserModel.firstName,
            UserModel.lastName,
            UserModel.avatarUrl,
        ) \
            .filter(PaymentModel.id_need==self.id) \
            .filter(PaymentModel.id_user==UserModel.id) \
            .filter(PaymentModel.is_verified==True) \
            .group_by(
                PaymentModel.id_user,
                PaymentModel.id_need,
                UserModel.firstName,
                UserModel.lastName,
                UserModel.avatarUrl,
            ) \

        participants = []
        for participant in participants_query:
            participants.append(dict(
                contribution=participant[0],
                userFirstName=participant[1],
                userLastName=participant[2],
                avatarUrl=participant[3],
            ))

        return participants

    @participants.expression
    def participants(cls):
        pass

    def get_ccs(self):
        return {
            member.user.emailAddress
            for member in self.child.families[0].current_members()
        }

    def get_participants(self):
        from say.models.need_family_model import NeedFamilyModel
        session = object_session(self)

        return session.query(NeedFamilyModel) \
            .filter_by(id_need=self.id) \
            .filter_by(isDeleted=False) \

    def update(self):
        from say.utils import digikala
        data = digikala.get_data(self.link)

        dkp = data['dkp']
        img = data['img']
        title = data['title']
        cost = data['cost']

        if img:
            self.img = img

        if title:
            self.title = title

        if cost:
            if type(cost) is int:
                self.cost = cost
            elif type(cost) is str:
                session = object_session(self)

                from say.api import app
                from say.models import NgoModel

                SAY_ngo = session.query(NgoModel).filter_by(name='SAY').first()
                if child.ngo.name != SAY_ngo.name:
                    with app.app_context():
                        send_email.delay(
                            subject=f'تغییر وضعیت کالا {dkp}',
                            emails=SAY_ngo.coordinator.emailAddress,
                            html=render_template(
                                'product_status_changed.html',
                                 child=self.child,
                                 need=self,
                                 dkp=dkp,
                                 details=cost,
                            ),
                        )
        return data

    def send_done_email(self):
        cc_emails = self.get_ccs()
        to_emails = set()

        participants = self.get_participants()
        for participate in participants:
            to_emails.add(participate.user.emailAddress)

        cc_emails -= to_emails

        iran_date = JalaliDate(self.doneAt).localdateformat()
        send_email.delay(
            subject=f'یکی از نیازهای {self.child.sayName} کامل شد',
            emails=list(to_emails),
            cc=list(cc_emails),
            html=render_template(
                'status_done.html',
                child=self.child,
                need=self,
                date=iran_date,
            ),
        )

    def send_purchase_email(self):
        cc_emails = self.get_ccs()
        to_emails = set()

        participants = self.get_participants()
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
        cc_emails = self.get_ccs()
        to_emails = set()

        participants = self.get_participants()
        for participate in participants:
            to_emails.add(participate.user.emailAddress)

        cc_emails -= to_emails
        iran_date = JalaliDate(datetime.utcnow()).localdateformat()

        from say.api import app
        deliver_to_child_delay = datetime.utcnow() \
            + timedelta(seconds=app.config['DELIVER_TO_CHILD_DELAY'])
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
            eta=deliver_to_child_delay,
        )
        from say.tasks.update_needs import change_need_status_to_delivered
        change_need_status_to_delivered.apply_async(
            (self.id,),
            eta=deliver_to_child_delay,
        )

    def send_child_delivery_service_email(self):
        cc_emails = self.get_ccs()
        to_emails = set()

        participants = self.get_participants()
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
        cc_emails = self.get_ccs()
        to_emails = set()

        participants = self.get_participants()
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

