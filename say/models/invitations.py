import secrets
import uuid

from wtforms_alchemy import ModelForm

from . import *


class Invitation(base, Timestamp):
    __tablename__ = 'invitations'

    id = Column(Integer, nullable=False, primary_key=True)
    family_id = Column(Integer, ForeignKey('family.id'), nullable=False)
    role = Column(Integer, nullable=False)
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


class InvitationForm(ModelForm):
    class Meta:
        model = Invitation

        only = ['family_id', 'role']


