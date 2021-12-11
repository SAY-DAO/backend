from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from say.orm import base


class BaseUser(base):
    __tablename__ = 'base_users'

    id = Column(Integer, primary_key=True)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'base_user',
        'polymorphic_on': type,
    }
