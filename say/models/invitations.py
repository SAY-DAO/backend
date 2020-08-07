import secrets
from urllib.parse import urljoin

from . import *
from ..api import app
from say.constants import ALPHABET


# FIXME: Collision
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
    see_count = Column(Integer, default=0, nullable=False)
    text = Column(Unicode(128), nullable=True)
    token = Column(
        Unicode(128),
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

    @hybrid_property
    def link(self):
        return urljoin(
            app.config['BASE_URL'], f'/search-result?token={self.token}',
        )

    @link.expression
    def link(cls):
        return None
