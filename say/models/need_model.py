from decimal import Decimal
from datetime import datetime, timedelta

from khayyam import JalaliDate
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.orm import object_session
from sqlalchemy import event

from say.statuses import NeedStatuses
from say.api import render_template, int_formatter
from say.tasks import send_email, send_embeded_subject_email

from .payment_model import Payment
from . import *

"""
Need Model
"""


class Need(base, Timestamp):
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
    doneAt = Column(DateTime, nullable=True)
    purchase_date = Column(DateTime)
    expected_delivery_date = Column(DateTime)
    ngo_delivery_date = Column(DateTime)
    child_delivery_date = Column(DateTime)
    confirmDate = Column(DateTime, nullable=True)

    # TODO: Change this to @observers
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
        return cls.paid / cls.cost * 100

    @hybrid_property
    def isDone(self):
        return self.status >= 2

    '''
    aggregated generated query:
UPDATE need SET paid=(
    SELECT coalesce(
        sum(payment.need_amount),
        , 0
    ) AS coalesce_1
    FROM payment
    WHERE need.id = payment.id_need AND payment.verified IS NOT NULL)
WHERE need.id IN (502);
    '''
    @aggregated('payments', Column(Integer, nullable=False, default=0))
    def paid(cls):
        from . import Payment
        return coalesce(
            func.sum(Payment.need_amount),
            0,
        )

    @aggregated('payments', Column(Integer, nullable=False, default=0))
    def donated(cls):
        from . import Payment
        return coalesce(
            func.sum(Payment.donation_amount),
            0,
        )

    @observes('payments.verified')
    def payments_observer(self, _):
        session = object_session(self)
        if self.status > 2:
            return

        paid = sum(
            payment.need_amount if payment.verified else 0
            for payment in self.payments
        )

        if paid == 0:
            self.status = 0

        elif paid < self.cost:
            self.status = 1

        elif paid == self.cost:
            self.done()

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

    child = relationship(
        'Child',
        foreign_keys=child_id,
        uselist=False,
        back_populates='needs',
        lazy='selectin',
    )

    payments = relationship(
        'Payment',
        back_populates='need',
        primaryjoin=
            'and_(Need.id==Payment.id_need, Payment.verified.isnot(None))',
    )

    participants = relationship(
        'NeedFamily',
        back_populates='need',
        primaryjoin='and_(Need.id==NeedFamily.id_need, ~NeedFamily.isDeleted)',
    )

    def done(self):
        self.status = 2
        self.doneAt = datetime.utcnow()

    # TODO: Remove this and replace it with participants model
    def get_participants(self):
        from .user_model import User
        from .payment_model import Payment

        session = object_session(self)
        participants_query = session.query(
            func.sum(Payment.need_amount),
            User.firstName,
            User.lastName,
            User.avatarUrl,
        ) \
            .filter(Payment.id_need==self.id) \
            .filter(Payment.id_user==User.id) \
            .filter(Payment.verified.isnot(None)) \
            .group_by(
                Payment.id_user,
                Payment.id_need,
                User.firstName,
                User.lastName,
                User.avatarUrl,
            )

        participants = []
        for participant in participants_query:
            participants.append(dict(
                contribution=participant[0],
                userFirstName=participant[1],
                userLastName=participant[2],
                avatarUrl=participant[3],
            ))

        return participants

    @property
    def family(self):
        return {
            member.user
            for member in self.child.family.current_members()
        }

    def refund_extra_credit(self):
        # There is nothing to refund
        if self.cost >= self.paid:
            return

        total_refund = Decimal(self.paid) - Decimal(self.cost)

        for participant in self.participants:

            participation_ratio = Decimal(participant.paid) / Decimal(self.paid)

            refund_amount = Decimal(participation_ratio) * Decimal(total_refund)
            if refund_amount <= 0:
                continue

            refund_payment = Payment(
                need=self,
                user=participant.user,
                need_amount=-refund_amount,
                credit_amount=-refund_amount,
                desc='Refund payment',
            )
            self.payments.append(refund_payment)
            refund_payment.verify()

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
                from say.models import Ngo

                SAY_ngo = session.query(Ngo).filter_by(name='SAY').first()
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




@event.listens_for(Need.status, "set")
def status_event(need, new_status, old_status, initiator):
    if new_status == old_status:
        return

    elif new_status == 4 and need.isReported != True:
        raise Exception('Need has not been reported to ngo yet')

    need.status_updated_at = datetime.utcnow()

    if need.status == 2:
        need.done()

    elif need.type == 0:  # Service
        if new_status == 3:
            need.ngo_delivery_date = datetime.utcnow()

        elif new_status == 4:
            need.child_delivery_date = datetime.utcnow()
            need.child_delivery_product()
            need.refund_extra_credit()

    elif need.type == 1:  # Product
        if new_status == 3:
            need.purchase_date = datetime.utcnow()

        elif new_status == 4:
            need.ngo_delivery_date = parse_datetime(
                request.form.get('ngo_delivery_date')
            )

            if not (
                need.expected_delivery_date
                <= need.ngo_delivery_date <=
                datetime.utcnow()
            ):
                raise Exception('Invalid ngo_delivery_date')

            need.refund_extra_credit()


