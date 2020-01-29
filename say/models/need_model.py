from datetime import datetime, timedelta

from khayyam import JalaliDate
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import object_session

from say.statuses import NeedStatuses
from say.api import render_template, int_formatter
from say.tasks import send_email, send_embeded_subject_email
from . import *

"""
Need Model
"""


class NeedModel(base):
    __tablename__ = "need"

    id = Column(Integer, nullable=False, primary_key=True, unique=True)

    child_id = Column(Integer, ForeignKey('child.id'))

    name_translations = Column(HSTORE)
    name = translation_hybrid(name_translations)

    description_translations = Column(HSTORE)
    description = translation_hybrid(description_translations)

    imageUrl = Column(String, nullable=False)
    category = Column(Integer, nullable=False)  # 0:Growth | 1:Joy | 2:Health | 3:Surroundings
    isUrgent = Column(Boolean, nullable=False)
    details = Column(Text, nullable=True)
    _cost = Column(Integer, nullable=False)
    paid = Column(Integer, nullable=False, default=0)
    donated = Column(Integer, nullable=False, default=0)
    link = Column(String, nullable=True)
    affiliateLinkUrl = Column(String, nullable=True)
    isDone = Column(Boolean, nullable=False, default=False)
    isDeleted = Column(Boolean, nullable=False, default=False)
    receipts = Column(String, nullable=True)  # comma separated
    isConfirmed = Column(Boolean, nullable=False, default=False)
    confirmUser = Column(Integer, nullable=True)
    type = Column(Integer, nullable=False)  # 0:service | 1:product
    doing_duration = Column(Integer, nullable=False, default=5)
    status = Column(Integer, nullable=False, default=0)
    status_updated_at = Column(DateTime, nullable=True)
    isReported = Column(Boolean, default=False)
    img = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    oncePurchased = Column(Boolean, nullable=False, default=False)
    # Dates:
    createdAt = Column(DateTime, nullable=False)
    lastUpdate = Column(DateTime, nullable=False)
    doneAt = Column(DateTime, nullable=True)
    purchase_date = Column(DateTime)
    expected_delivery_date = Column(DateTime)
    ngo_delivery_date = Column(DateTime)
    child_delivery_date = Column(DateTime)
    confirmDate = Column(DateTime, nullable=True)

    child = relationship(
        'ChildModel',
        foreign_keys=child_id,
        uselist=False,
        back_populates='needs',
        lazy='selectin',
    )
    payments = relationship('PaymentModel', back_populates='need')
    need_family = relationship(
        'NeedFamilyModel',
        uselist=False,
        back_populates='need',
    )

    @hybrid_property
    def childSayName(self):
        return self.child.sayName

    @childSayName.expression
    def childSayName(cls):
        pass

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
    def pretty_cost(self):
        return int_formatter(self.cost)

    # TODO: proper expression
    @pretty_cost.expression
    def pretty_cost(cls):
        pass

    @hybrid_property
    def pretty_paid(self):
        return int_formatter(self.paid)

    # TODO: proper expression
    @pretty_paid.expression
    def pretty_paid(cls):
        pass

    @hybrid_property
    def pretty_donated(self):
        return int_formatter(self.donated)

    # TODO: proper expression
    @pretty_paid.expression
    def pretty_donated(self):
        pass

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

    @hybrid_property
    def type_name(self):
        if self.type == 0:
            return 'service'
        elif self.type == 1:
            return 'product'

        return 'unknown'

    @type_name.expression
    def type_name(cls):
        pass

    @hybrid_property
    def status_description(self):
        locale = get_locale()
        return NeedStatuses.get(self.status, self.type_name, locale)

    @status_description.expression
    def status_description(cls):
        pass

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

    @property
    def family(self):
        return [
            member.user
            for member in self.child.families[0].current_members()
        ]

    def get_participants(self):
        from say.models.need_family_model import NeedFamilyModel
        session = object_session(self)

        return session.query(NeedFamilyModel) \
            .filter_by(id_need=self.id) \
            .filter_by(isDeleted=False)

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
                if self.child.ngo.name != SAY_ngo.name:
                    with app.app_context():
                        send_email.delay(
                            subject=f'تغییر وضعیت کالا {dkp}',
                            to=SAY_ngo.coordinator.emailAddress,
                            html=render_template(
                                'product_status_changed.html',
                                child=self.child,
                                need=self,
                                dkp=dkp,
                                details=cost,
                            ),
                        )
        return data

    def child_delivery_product(self):
        from say.api import app
        from say.tasks.update_needs import change_need_status_to_delivered

        deliver_to_child_delay = datetime.utcnow() \
            + timedelta(seconds=app.config['DELIVER_TO_CHILD_DELAY'])

        change_need_status_to_delivered.apply_async(
            (self.id,),
            eta=deliver_to_child_delay,
        )


@event.listens_for(NeedModel.status, "set")
def status_event(need, new_status, old_status, initiator):
    if new_status == old_status:
        return

    need.status_updated_at = datetime.utcnow()

