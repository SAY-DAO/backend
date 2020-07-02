from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.orm import object_session

from . import *
from .need_family_model import NeedFamily
from .payment_model import Payment
from .user_model import User
from say.api import app
from say.statuses import NeedStatuses
from say.constants import DIGIKALA_TITLE_SEP


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
    purchase_cost = Column(Integer, nullable=False, default=0)
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
    bank_track_id = Column(Unicode(30), nullable=True) # Only for services

    # product
    unavailable_from = Column(DateTime, nullable=True)

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
    def unpayable(self):
        return bool(self.unavailable_from \
            and self.unavailable_from < datetime.utcnow() \
                - timedelta(days=app.config['PRODUCT_UNPAYABLE_PERIOD'])
        )

    @unpayable.expression
    def unpayable(cls):
        return cls.unavailable_from \
            and cls.unavailable_from < datetime.utcnow() \
                - timedelta(days=app.config['PRODUCT_UNPAYABLE_PERIOD'])

    @hybrid_property
    def unpayable_from(self):
        if not self.unavailable_from:
            return None

        return self.unavailable_from \
            + timedelta(days=app.config['PRODUCT_UNPAYABLE_PERIOD'])

    @unpayable_from.expression
    def unpayable_from(cls):
        if not cls.unavailable_from:
            return None

        return cls.unavailable_from \
            + timedelta(days=app.config['PRODUCT_UNPAYABLE_PERIOD'])

    @hybrid_property
    def progress(self):
        if self.isDone:
            return 100

        try:
           return str(format(self.paid / self.cost * 100, '.1f')) \
               .rstrip('0') \
               .rstrip('.')

        except:
            return 0

    @progress.expression
    def progress(cls):
        return cls.paid / cls.cost * 100

    @hybrid_property
    def isDone(self):
        return self.status >= 2

    '''
    aggregated generates query like this:
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
    def payments_observer(self, verification_dates):
        session = object_session(self)
        if len(verification_dates) == 0 or self.status is None or self.status >= 2:
            return

        paid = sum(
            payment.need_amount if payment.verified else 0
            for payment in self.payments
        )

        if paid < self.cost:
            self.status = 1

        elif paid == self.cost:
            self.done()

    @hybrid_property
    def clean_title(self):
        if self.title is None:
            return None

        for word in self.title.split(' '):
            if word in DIGIKALA_TITLE_SEP:
                return self.title[: self.title.find(word)].strip()

        return self.title

    @clean_title.expression
    def clean_title(cls):
        pass

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
        raw_status = NeedStatuses.get(self.status, self.type_name, locale)
        need_name = self.clean_title if self.type == 1 else self.name

        if self.status == 2 or (self.type == 1 and self.status == 3):
            '''
            p2s2p3 need status condition
            تمام هزینه سرویس/کالا پرداخت شده است
            کالا خریداری شده است و به زودی توسط دیجی‌کالا به انجمن می‌رسد
            '''
            return raw_status % need_name

        elif (self.type == 1 and self.status == 5) or (self.type == 0 and self.status == 4):
            '''
            p5s4 need status condition
            کالا به دست اصغر رسید
            هزینه سرویس برای اصغر تمام و کمال پرداخت شد
            '''
            return raw_status % (need_name, self.childSayName)

        elif self.type == 0 and self.status == 3:
            '''
            s3 need status condition
            مبلغ 2000 تومان به حساب انجمن واریز شده است تا هزینه سرویس پرداخت شود
            '''
            return raw_status % (self.pretty_cost, need_name)

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
        lazy='selectin',
    )

    def done(self):
        self.status = 2
        self.doneAt = datetime.utcnow()

    @property
    def family(self):
        return {
            member.user
            for member in self.child.family.current_members()
        }

    def refund_extra_credit(self, new_paid):
        session = object_session(self)
        total_refund = Decimal(self.paid) - Decimal(new_paid)

        if total_refund <= 0:
            return

        participants = session.query(NeedFamily) \
            .filter(NeedFamily.id_need == self.id)

        total_reminder = Decimal(0)
        refunds = []
        for participant in participants:
            participation_ratio = Decimal(participant.paid) / Decimal(self.paid)
            refund_amount = Decimal(participation_ratio) * Decimal(total_refund)

            if refund_amount <= 0:
                continue

            reminder = refund_amount - int(refund_amount)
            total_reminder += reminder
            refund_amount = refund_amount - reminder

            refund_payment = Payment(
                need=self,
                user=participant.user,
                need_amount=-refund_amount,
                credit_amount=-refund_amount,
                desc='Refund payment',
            )

            refunds.append(refund_payment)

        min_refund = min(refunds, key=lambda r: -r.need_amount)
        min_refund.need_amount -= total_reminder
        min_refund.credit_amount -= total_reminder

        for refund in refunds:
            if refund.need_amount == 0:
                session.delete(refund)
                continue

            refund.verify()

        return

    def say_extra_payment(self):
        extra_cost = self.purchase_cost - self.paid

        session = object_session(self)
        say_user = session.query(User) \
            .filter_by(userName='SAY') \
            .one()

        say_payment = Payment(
            need=self,
            user=say_user,
            need_amount=extra_cost,
            desc='SAY payment',
        )

        self.payments.append(say_payment)
        say_payment.verify(is_say=True)

        return

    @property
    def current_participants(self):
        for p in self.participants:
            if p.isDeleted:
                continue

            yield p

        past_participation, = session.query(
            func.sum(NeedFamily.paid)
        ) \
            .filter(NeedFamily.id_need==self.id) \
            .filter(NeedFamily.isDeleted==True) \
            .first()

        if past_participation:
            yield NeedFamily(
                user_role=-1,
                paid=past_participation,
            )

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

        if type(cost) is int:
            if not self.isDone:
                self.cost = cost
                self.purchase_cost = cost
            self.change_availability(True)
        else:
            self.change_availability(False)

        return data

    def child_delivery_product(self):
        from say.api import app
        from say.tasks import change_need_status_to_delivered

        deliver_to_child_delay = datetime.utcnow() \
            + timedelta(seconds=app.config['DELIVER_TO_CHILD_DELAY'])

        change_need_status_to_delivered.apply_async(
            (self.id,),
            eta=deliver_to_child_delay,
        )

    def change_cost(self, new_cost):
        self.cost = new_cost

        if self.cost <= self.paid:
            self.refund_extra_credit(self.cost)
            if not self.isDone:
                self.done()

        else:
            raise NotImplementedError('cost > paid')
        # TODO: When cost > paid?

    def change_availability(self, is_):
        if is_:
            self.unavailable_from = None
        else:
            if not self.unavailable_from:
                self.unavailable_from = datetime.utcnow()


@event.listens_for(Need.status, "set")
def status_event(need, new_status, old_status, initiator):

    if new_status == 4 and need.isReported != True:
        raise Exception('Need has not been reported to ngo yet')

    need.status_updated_at = datetime.utcnow()

    if need.type == 0:  # Service
        if new_status == 3:
            need.ngo_delivery_date = datetime.utcnow()

        elif new_status == 4:
            need.child_delivery_date = datetime.utcnow()

    elif need.type == 1:  # Product
        if new_status == 3:
            need.purchase_date = datetime.utcnow()

        elif new_status == 4:
            if old_status == new_status:
                return

            need.ngo_delivery_date = parse_datetime(
                request.form.get('ngo_delivery_date')
            )

            if not (
                need.expected_delivery_date
                <= need.ngo_delivery_date <=
                datetime.utcnow()
            ):
                raise Exception('Invalid ngo_delivery_date')

            need.child_delivery_product()

            if need.purchase_cost < need.paid:
                need.refund_extra_credit(need.purchase_cost)

            elif need.purchase_cost > need.paid:
                need.say_extra_payment()

            need.cost = need.purchase_cost

