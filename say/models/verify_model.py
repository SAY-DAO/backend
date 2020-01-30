from datetime import datetime, timedelta
from . import *
from sqlalchemy import DateTime


def expire_at():
    return datetime.utcnow() + timedelta(minutes=2)


"""
Verify Model
"""


class Verification(base, Timestamp):
    __tablename__ = "verify"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    code = Column(Integer, nullable=False)
    expire_at = Column(DateTime, nullable=False, default=expire_at)

    user = relationship("User", foreign_keys=user_id)
