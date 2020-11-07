from sqlalchemy import Column, Integer, Unicode, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.relationships import foreign
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import Timestamp

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
