from sqlalchemy.ext.associationproxy import association_proxy
from pydantic import BaseModel as PydanticBaseModel

from . import *


class UserInvitation(base, Timestamp):
    __tablename__ = 'user_invitation'

    id = Column(Integer, nullable=False, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable=False,
    )

    invitation_id = Column(
        Integer,
        ForeignKey('invitations.id'),
        nullable=False,
    )

    role = Column(Integer, nullable=True)
    status = Column(String(10), nullable=False)

    user = relationship('User', foreign_keys=user_id, uselist=False)
    invitation = relationship(
        'Invitation', foreign_keys=invitation_id, uselist=False,
    )

    # invited_username = association_proxy('user', 'userName')
    # invited_by_username = association_proxy('invitation', 'invited_by.userName')
    # family_id = association_proxy('invitation', 'family_id')
    # token = association_proxy('invitation', 'token')

    __mapper_args__ = {
        'polymorphic_on': status,
    }


class PendingInvitation(UserInvitation):

    __mapper_args__ = {
        'polymorphic_identity': 'pending',
    }

    def accept(self):
        self.status = 'accepted'


class AcceptedInvitation(UserInvitation):

    __mapper_args__ = {
        'polymorphic_identity': 'accepted',
    }


class RejectedInvitation(UserInvitation):

    __mapper_args__ = {
        'polymorphic_identity': 'rejected',
    }


