from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.orm import column_property
from sqlalchemy.orm import object_session

from say.constants import DIGIKALA_TITLE_SEP
from say.constants import SAY_USER
from say.date import parse_date
from say.orm.types import ResourceURL
from say.statuses import NeedStatuses

from ..config import configs
from . import *
from .need_family_model import NeedFamily
from .payment_model import Payment
from .receipt import NeedReceipt


"""
Need Model
"""


class Need(base, Timestamp):
    __tablename__ = "need"

    id = Column(Integer, nullable=False, primary_key=True, unique=True)

    child_id = Column(Integer, ForeignKey('child.id'), index=True)
    created_by_id = Column(Integer, ForeignKey('social_worker.id'), nullable=True)

    name_translations = Column(HSTORE)
    name = translation_hybrid(name_translations)

    description_translations = Column(HSTORE)
    description = translation_hybrid(description_translations)

    imageUrl = Column(ResourceURL, nullable=False)
    category = Column(
        Integer, nullable=False
    )  # 0:Growth | 1:Joy | 2:Health | 3:Surroundings
    isUrgent = Column(Boolean, nullable=False)
    details = Column(Text, nullable=True)
    informations = Column(String(1024), nullable=True)
    _cost = Column(Integer, nullable=False)
    purchase_cost = Column(Integer, nullable=True)
    link = Column(String, nullable=True)
    affiliateLinkUrl = Column(String, nullable=True)
    # isDone = Column(Boolean, nullable=False, default=False, index=True)
    isDeleted = Column(Boolean, nullable=False, default=False, index=True)
    receipts = Column(String, nullable=True)  # comma separated
    isConfirmed = Column(Boolean, nullable=False, default=False, index=True)
    confirmUser = Column(Integer, nullable=True)
    type = Column(Integer, nullable=False, index=True)  # 0:service | 1:product
    doing_duration = Column(Integer, nullable=False, default=5)
    status = Column(Integer, nullable=False, default=0, index=True)
    status_updated_at = Column(DateTime, nullable=True)
    isReported = Column(Boolean, default=False, index=True)
    img = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    oncePurchased = Column(Boolean, nullable=False, default=False, index=True)
    bank_track_id = Column(Unicode(30), nullable=True)  # Only for services
    # product
    unavailable_from = Column(DateTime, nullable=True)
    # Dates:
    doneAt = Column(DateTime, nullable=True)
    purchase_date = Column(DateTime)
    # Digikala purchase code
    dkc = Column(String(20), nullable=True)
    expected_delivery_date = Column(DateTime)
    ngo_delivery_date = Column(DateTime)
    child_delivery_date = Column(DateTime)
    confirmDate = Column(DateTime, nullable=True)

    deleted_at = Column(DateTime, nullable=True)
    unconfirmed_at = Column(DateTime, nullable=True)

    paid = column_property(
        select([coalesce(func.sum(Payment.need_amount), 0,)]).where(
            and_(
                Payment.verified.isnot(None),
                Payment.id_need == id,
            )
        )
    )

    donated = column_property(
        select([coalesce(func.sum(Payment.donation_amount), 0,)]).where(
            and_(
                Payment.verified.isnot(None),
                Payment.id_need == id,
            )
        )
    )

    receipt_count = column_property(
        select([coalesce(func.count(1), 0)]).where(
            and_(
                NeedReceipt.need_id == id,
                NeedReceipt.deleted.is_(None),
            )
        )
    )

    @property
    def is_reported(self):
        return self.isReported

    @is_reported.setter
    def is_reported(self, value):
        self._x = value

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
    def unpaid_cost(self):
        return self.cost - self.paid

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
    def pretty_donated(cls):
        pass

    @hybrid_property
    def unpayable(self):
        return bool(
            self.unavailable_from
            and self.unavailable_from
            < datetime.utcnow()
            - timedelta(
                days=configs.PRODUCT_UNPAYABLE_PERIOD,
            )
        )

    @unpayable.expression
    def unpayable(cls):
        return and_(
            cls.unavailable_from.isnot(None),
            cls.unavailable_from
            < datetime.utcnow() - timedelta(days=configs.PRODUCT_UNPAYABLE_PERIOD),
        )

    @hybrid_property
    def unpayable_from(self):
        if not self.unavailable_from:
            return None

        return self.unavailable_from + timedelta(days=configs.PRODUCT_UNPAYABLE_PERIOD)

    @unpayable_from.expression
    def unpayable_from(cls):
        if not cls.unavailable_from:
            return None

        return cls.unavailable_from + timedelta(days=configs.PRODUCT_UNPAYABLE_PERIOD)

    @hybrid_property
    def progress(self):
        if self.isDone:
            return 100

        try:
            return str(format(self.paid / self.cost * 100, '.1f')).rstrip('0').rstrip('.')

        except:
            return 0

    @progress.expression
    def progress(cls):
        return cls.paid / cls.cost * 100

    @hybrid_property
    def isDone(self):
        return self.status >= 2

    @hybrid_property
    def is_done(self):
        return self.cost == self.paid

    @hybrid_property
    def clean_title(self):
        if self.title is None:
            return self.name

        for word in self.title.split(' '):
            if word in DIGIKALA_TITLE_SEP:
                keyword_index = self.title.find(word)
                if keyword_index == 0:
                    continue

                return self.title[:keyword_index].strip()

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

        elif (self.type == 1 and self.status == 5) or (
            self.type == 0 and self.status == 4
        ):
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
    )

    carts = relationship(
        'CartNeed',
        back_populates='need',
    )

    payments = relationship(
        'Payment',
        back_populates='need',
    )

    participants = relationship(
        'NeedFamily',
        back_populates='need',
    )

    receipts_ = relationship(
        'Receipt',
        secondary='need_receipt',
        back_populates='needs',
    )

    def done(self):
        self.status = 2
        self.doneAt = datetime.utcnow()
        self.delete_from_carts()

    @property
    def family(self):
        return {member.user for member in self.child.family.current_members()}

    def delete_from_carts(self):
        for cart in self.carts:
            cart.deleted = datetime.utcnow()

    def refund_extra_credit(self, new_paid):
        session = object_session(self)
        total_refund = Decimal(self.paid) - Decimal(new_paid)

        if total_refund <= 0:
            return

        participants = session.query(NeedFamily).filter(NeedFamily.id_need == self.id)

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

        return refunds

    def say_extra_payment(self):
        from .user_model import User

        extra_cost = self.purchase_cost - self.paid
        session = object_session(self)
        say_user = session.query(User).filter_by(userName=SAY_USER).one()

        say_payment = Payment(
            need=self,
            user=say_user,
            need_amount=extra_cost,
            desc='SAY payment',
        )

        self.payments.append(say_payment)
        say_payment.verify(is_say=True)

        return say_payment

    @property
    def current_participants(self):
        past_participation = NeedFamily(
            user_role=-1,
            paid=0,
        )

        for p in self.participants:
            if p.isDeleted:
                past_participation.paid += p.paid
                continue

            yield p

        if past_participation.paid != 0:
            yield NeedFamily(
                user_role=-1,
                paid=past_participation.paid,
            )

    def update(self, force=False):
        from say.crawler import Crawler
        from say.crawler import DigikalaCrawler

        if 'digikala' in self.link:
            data = DigikalaCrawler(self.link).get_data(force=force)
        else:
            data = Crawler(self.link).get_data(force=force)

        if data is None:
            return

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

            self.change_availability(True)
        else:
            self.change_availability(False)

        return data

    def delivere_to_child(self):
        assert self.status == 4 and self.type == 1 and self.ngo_delivery_date is not None

        self.status = 5
        self.child_delivery_date = self.ngo_delivery_date + timedelta(
            seconds=configs.DELIVER_TO_CHILD_DELAY
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

    def unconfirm(self):
        self.refund_extra_credit(0)
        self.purchase_cost = None
        self.confirmDate = None
        self.confirmUser = None
        self.isConfirmed = False
        self.status = 0
        self.unconfirmed_at = datetime.utcnow()
        self.delete_from_carts()
        for participant in self.participants:
            participant.isDeleted = True

    def delete(self):
        assert self.status < 4
        self.unconfirm()
        self.isDeleted = True
        self.deleted_at = datetime.utcnow()


@event.listens_for(Need.status, "set")
def status_event(need, new_status, old_status, initiator):

    if new_status == 4 and need.isReported != True:
        raise Exception('Need has not been reported to ngo yet')

    need.status_updated_at = datetime.utcnow()

    if need.type == 0:  # Service
        if new_status == 3:
            need.ngo_delivery_date = datetime.utcnow()

        elif new_status == 4:
            if old_status == new_status:
                return

            if need.purchase_cost < need.paid:
                need.refund_extra_credit(need.purchase_cost)

            elif need.purchase_cost > need.paid:
                need.say_extra_payment()

            need.cost = need.purchase_cost
            need.child_delivery_date = datetime.utcnow()

    elif need.type == 1:  # Product
        if new_status == 3:
            need.purchase_date = datetime.utcnow()

        elif new_status == 4:
            if old_status == new_status:
                return

            need.ngo_delivery_date = parse_date(request.form.get('ngo_delivery_date'))

            if (
                need.ngo_delivery_date < need.expected_delivery_date
                or need.ngo_delivery_date > datetime.utcnow()
            ):
                raise Exception('Invalid ngo_delivery_date')

            if need.purchase_cost < need.paid:
                need.refund_extra_credit(need.purchase_cost)

            elif need.purchase_cost > need.paid:
                need.say_extra_payment()

            need.cost = need.purchase_cost
