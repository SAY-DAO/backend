import secrets
import uuid
from urllib.parse import urljoin

from . import *
from ..api import app


class Invitation(base, Timestamp):
    __tablename__ = 'invitations'

    id = Column(Integer, nullable=False, primary_key=True)
    family_id = Column(Integer, ForeignKey('family.id'), nullable=False)
    role = Column(Integer, nullable=True)
    see_count = Column(Integer, default=0, nullable=False)
    text = Column(Unicode(128), nullable=True)

    token = Column(
        Unicode(128),
        default=lambda: str(uuid.uuid4()) + secrets.token_urlsafe(),
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

    @hybrid_property
    def link(self):
        return urljoin(
            app.config['BASE_URL'], f'/search-result?token={self.token}',
        )

    @link.expression
    def link(cls):
        return None
