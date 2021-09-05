import enum
import secrets
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.sqltypes import Unicode

from say.constants import ALPHABET

from ..orm import base


def generate_token():
    return ''.join(secrets.choice(ALPHABET) for i in range(8))


class SearchType(enum.Enum):
    random = 'random'
    brain = 'brain'


class Search(base):
    __tablename__ = 'search'

    id = Column(Integer, primary_key=True)

    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    child_id = Column(Integer, ForeignKey('child.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    type = Column(Enum(SearchType), default=SearchType.random)

    token = Column(
        Unicode(12),
        nullable=False,
        unique=True,
        index=True,
    )

    child = relationship(
        'Child',
        foreign_keys=child_id,
        uselist=False,
    )

    user = relationship(
        'User',
        foreign_keys=user_id,
        uselist=False,
    )
