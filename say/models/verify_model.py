from datetime import datetime, timedelta
from . import *
from sqlalchemy import DateTime
from say.models.user_model import UserModel


def expire_at():
    return datetime.utcnow() + timedelta(days=1)


"""
Verify Model
"""


class VerifyModel(base):
    __tablename__ = "verify"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_user = Column(Integer, ForeignKey(UserModel.id), nullable=False)
    code = Column(Integer, nullable=False)
    expire_at = Column(DateTime, nullable=False, default=expire_at)

    user = relationship("UserModel", foreign_keys=id_user)
