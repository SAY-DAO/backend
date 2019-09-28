from . import *
from say.models.user_model import UserModel


"""
Verify Model
"""


class VerifyModel(base):
    __tablename__ = "verify"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_user = Column(Integer, ForeignKey(UserModel.id), nullable=False)
    verify_code = Column(Integer, nullable=False)

    user = relationship("UserModel", foreign_keys=id_user)
