import secrets
from urllib.parse import urljoin

from say.models import *
from say.constants import ALPHABET
from say.config import configs


# FIXME: Collision
TEXT_LENGHT = 512


def generate_token():
    return ''.join(secrets.choice(ALPHABET) for i in range(8))


class Invitation(base, Timestamp):
    __tablename__ = 'invitations'

    id = Column(Integer, nullable=False, primary_key=True)
    inviter_id = Column(
        Integer, ForeignKey('user.id'), nullable=True, index=True,
    )
    family_id = Column(
        Integer, ForeignKey('family.id'), nullable=False, index=True,
    )

    role = Column(Integer, nullable=True)
    text = Column(Unicode(128), nullable=True)
    token = Column(
        Unicode(TEXT_LENGHT),
        default=lambda: generate_token(),
        nullable=False,
        unique=True,
        index=True,
    )

    family = relationship(
        'Family',
        back_populates='invitations',
        foreign_keys=family_id,
        uselist=False,
    )

    inviter = relationship(
        'User',
        back_populates='sent_invitations',
        foreign_keys=inviter_id,
        uselist=False,
    )

    accepts = relationship(
        'InvitationAccept',
        back_populates='invitation',
    )

    @hybrid_property
    def link(self):
        return urljoin(
            configs.BASE_URL, f'/search-result?token={self.token}',
        )

    @link.expression
    def link(cls):
        return None
