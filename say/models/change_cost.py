import enum
from typing import Optional

from pydantic import conint, constr
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Column, Integer, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import Timestamp

from ..constants import MAX_NEED_COST
from ..orm import base

DESCRIPTION_MAX_LENGTH = 128
REJECT_CAUSE_MAX_LENGTH = 128


class ChangeCostStatus(enum.Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'


class ChangeCostCreateSchema(PydanticBaseModel):
    to: conint(gt=-2, lt=MAX_NEED_COST)
    description: constr(max_length=DESCRIPTION_MAX_LENGTH) = ''


class ChangeCostRejectSchema(PydanticBaseModel):
    rejectCause: constr(max_length=REJECT_CAUSE_MAX_LENGTH) = ''


class ChangeCostAcceptSchema(PydanticBaseModel):
    reviewer_id: int
    to: Optional[conint(gt=-2, lt=MAX_NEED_COST)]
    description: Optional[constr(max_length=DESCRIPTION_MAX_LENGTH)]
    status: ChangeCostStatus


class ChangeCost(base, Timestamp):
    __tablename__ = 'change_cost'

    id = Column(Integer, primary_key=True)

    need_id = Column(Integer, ForeignKey('need.id'), nullable=False)
    requester_id = Column(
        Integer,
        ForeignKey('social_worker.id'),
        nullable=False,
    )
    reviewer_id = Column(
        Integer,
        ForeignKey('social_worker.id'),
        nullable=True,
    )

    status = Column(Enum(ChangeCostStatus), default=ChangeCostStatus.pending)
    from_ = Column(Integer, nullable=False)
    to = Column(Integer, nullable=False)
    description = Column(
        String(DESCRIPTION_MAX_LENGTH),
        nullable=False,
        default='',
    )
    reject_cause = Column(
        String(REJECT_CAUSE_MAX_LENGTH),
        nullable=False,
        default='',
    )

    need = relationship(
        'Need',
        foreign_keys=need_id,
        uselist=False,
    )


