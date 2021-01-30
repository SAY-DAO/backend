from logging import fatal
from sqlalchemy import Column, Integer, Unicode, Boolean, DateTime, ForeignKey, or_
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import Timestamp

from ..roles import *
from ..orm import base


class Receipt(base, Timestamp):
    __tablename__ = 'receipt'

    id = Column(Integer, primary_key=True)

    owner_id = Column(Integer, ForeignKey('social_worker.id'), nullable=False)

    attachment = Column(Unicode(128), nullable=False)
    code = Column(Unicode(64), nullable=False, index=True)
    deleted = Column(DateTime, nullable=True)
    description = Column(Unicode(1024), nullable=True)
    title = Column(Unicode(128), nullable=True)
    is_public = Column(Boolean, default=False)

    needs = relationship(
        'Need',
        secondary='need_receipt',
        back_populates='receipts_',
    )
        
    __table_args__ = (
        UniqueConstraint('code', 'deleted'),
    )

    @classmethod
    def _query(cls, session, role, user_id, ngo_id=-1, for_update=False, fields=None):
        from . import Need, Child

        query = session.query(cls).filter(cls.deleted.is_(None))
        if for_update:
            query = query.with_for_update()

        if fields:
            query = query.with_entities(*fields)

        if role in [SUPER_ADMIN, SAY_SUPERVISOR, ADMIN]:
            return query
        
        if role in [USER, None]:
            return query.filter(Receipt.is_public == True)

        return query \
            .join(NeedReceipt) \
            .join(Need) \
            .join(Child) \
            .filter(
                or_(
                    Child.id_social_worker == user_id,
                    Receipt.is_public == True if not for_update else False,
                    Child.id_ngo == ngo_id if role == NGO_SUPERVISOR else False,
                ),
                cls.is_public == False if for_update else True,
            )

class NeedReceipt(base, Timestamp):
    __tablename__ = 'need_receipt'

    id = Column(Integer, primary_key=True)

    need_id = Column(Integer, ForeignKey('need.id'), nullable=False)
    sw_id = Column(Integer, ForeignKey('social_worker.id'), nullable=False)
    receipt_id = Column(Integer, ForeignKey('receipt.id'), nullable=False)

    deleted = Column(DateTime, nullable=True)

    need = relationship(
        'Need',
        foreign_keys=need_id,
    )

    receipt = relationship(
        'Receipt',
        foreign_keys=receipt_id,
    )

    sw = relationship(
        'SocialWorker',
        foreign_keys=sw_id,
    )

    __table_args__ = (
        UniqueConstraint('need_id', 'receipt_id', 'deleted'),
    )
