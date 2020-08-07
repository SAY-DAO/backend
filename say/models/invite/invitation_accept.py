from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils import Timestamp

from say.orm import base


class InvitationAccept(base):
    __tablename__ = 'invitation_accepts'

    id = Column(Integer, primary_key=True)

    invtee_id = Column(
        Integer, ForeignKey('user.id'), nullable=False, index=True,
    )
    invitation_id = Column(
        Integer, ForeignKey('invitations.id'), nullable=False, index=True,
    )

    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    role = Column(Integer, nullable=False)

    invitee = relationship(
        'User',
        foreign_keys=invtee_id,
        uselist=False,
        back_populates='invitation_accepts',
    )
    invitation = relationship(
        'Invitation',
        foreign_keys=invitation_id,
        uselist=False,
        back_populates='accepts',
    )
