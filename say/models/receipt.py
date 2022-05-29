from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import or_
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import Timestamp

from say.roles import ADMIN
from say.roles import NGO_SUPERVISOR
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from say.roles import USER

from ..orm import base


class Receipt(base, Timestamp):
    __tablename__ = 'receipt'
    __versioned__ = {}

    id = Column(Integer, primary_key=True)

    owner_id = Column(Integer, ForeignKey('social_worker.id'), nullable=False, index=True)

    attachment = Column(Unicode(256), nullable=False)
    code = Column(Unicode(128), nullable=True, index=True)
    deleted = Column(DateTime, nullable=True)
    description = Column(Unicode(1024), nullable=True)
    title = Column(Unicode(128), nullable=False)
    is_public = Column(Boolean, default=False)
    need_status = Column(Integer, nullable=True)

    needs = relationship(
        'Need',
        secondary='need_receipt',
        back_populates='receipts_',
    )

    owner = relationship('SocialWorker', foreign_keys=[owner_id], uselist=False)

    __table_args__ = (UniqueConstraint('code', 'deleted'),)

    @classmethod
    def _query(cls, session, role, user_id, ngo_id=-1, for_update=False, fields=None):
        from . import Child
        from . import Need

        query = session.query(cls).filter(cls.deleted.is_(None))
        if for_update:
            query = query.with_for_update()

        if fields:
            query = query.with_entities(*fields)

        if role in [SUPER_ADMIN, SAY_SUPERVISOR, ADMIN]:
            return query

        if role in [USER, None]:
            return query.filter(Receipt.is_public.is_(True))

        return (
            query.join(NeedReceipt)
            .join(Need)
            .join(Child)
            .filter(
                or_(
                    Child.id_social_worker == user_id,
                    Receipt.is_public.is_(True) if not for_update else False,
                    Child.id_ngo == ngo_id if role == NGO_SUPERVISOR else False,
                ),
                cls.is_public.is_(False) if for_update else True,
            )
        )


class NeedReceipt(base, Timestamp):
    __tablename__ = 'need_receipt'

    id = Column(Integer, primary_key=True)

    need_id = Column(Integer, ForeignKey('need.id'), nullable=False, index=True)
    sw_id = Column(Integer, ForeignKey('social_worker.id'), nullable=False, index=True)
    receipt_id = Column(Integer, ForeignKey('receipt.id'), nullable=False, index=True)

    deleted = Column(DateTime, nullable=True)

    need = relationship(
        'Need',
        foreign_keys=[need_id],
        uselist=False,
    )

    receipt = relationship(
        'Receipt',
        foreign_keys=[receipt_id],
        uselist=False,
    )

    sw = relationship(
        'SocialWorker',
        foreign_keys=[sw_id],
        uselist=False,
    )

    __table_args__ = (UniqueConstraint('need_id', 'receipt_id', 'deleted'),)
