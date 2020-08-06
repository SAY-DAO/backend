import enum
import secrets
from datetime import datetime
from urllib.parse import urljoin

from sqlalchemy import Integer, Column, ForeignKey, Unicode, Enum, select, \
    DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, column_property
from sqlalchemy_utils.models import Timestamp

from say import config
from say.constants import alphabet, INVITATION_REJECT_REASON_LENGTH
from say.models import User
from say.orm import base


# FIXME: Collision
def generate_token():
    return ''.join(secrets.choice(alphabet) for i in range(8))


class InvitationStatus(enum.Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'


class Invitation(base, Timestamp):
    __tablename__ = 'invitations'

    id = Column(Integer, nullable=False, primary_key=True)
    family_id = Column(
        Integer, ForeignKey('family.id'), index=True, nullable=False,
    )
    inviter_id = Column(
        Integer, ForeignKey('user.id'), index=True, nullable=False,
    )
    invitee_id = Column(
        Integer, ForeignKey('user.id'), index=True, nullable=True,
    )
    invitee_username = column_property(
        select([User.userName])
        .where(User.id == invitee_id)
        .correlate_except(User)
    )
    role = Column(Integer, nullable=True)
    see_count = Column(Integer, default=0, nullable=False)
    status = Column(
        Enum(InvitationStatus),
        nullable=False,
        default=InvitationStatus.pending,
        index=True,
    )
    accepted_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    reject_reason = Column(
        Unicode(INVITATION_REJECT_REASON_LENGTH), nullable=True,
    )

    # FIXME: Reduce size
    token = Column(
        Unicode(128),
        default=lambda: generate_token(),
        nullable=False,
        index=True,
    )

    @hybrid_property
    def link(self):
        return urljoin(config['BASE_URL'], f'search-result?token={self.token}')

    @link.expression
    def link_expr(self):
        return None

    inviter = relationship(
        'User',
        foreign_keys=inviter_id,
        uselist=False,
    )

    invitee = relationship(
        'User',
        foreign_keys=invitee_id,
        uselist=False,
    )

    family = relationship(
        'Family',
        back_populates='invitations',
        foreign_keys=family_id,
        uselist=False,
    )

    def accept(self):
        assert self.status == InvitationStatus.pending.value

        self.status = InvitationStatus.accepted.value
        self.accepted_at = datetime.utcnow()
        self.reject_reason = None
        self.rejected_at = None

    def reject(self, reason):
        assert self.status == InvitationStatus.pending.value

        self.status = InvitationStatus.rejected.value
        self.rejected_at = datetime.utcnow()
        self.reject_reason = reason
        self.accepted_at = None
