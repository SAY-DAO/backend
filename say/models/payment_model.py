from say.models.need_model import NeedModel
from say.models.user_model import UserModel
from . import *

"""
Payment Model
"""


class PaymentModel(base):
    __tablename__ = "payment"

    id = Column(Integer, nullable=False, primary_key=True)
    id_need = Column(Integer, ForeignKey(NeedModel.id), nullable=False)
    id_user = Column(Integer, ForeignKey(UserModel.id), nullable=False)
    amount = Column(Integer, nullable=False)
    createdAt = Column(Date, nullable=False)

    need_relation = relationship("NeedModel", foreign_keys="PaymentModel.id_need")
    user_relation = relationship("UserModel", foreign_keys="PaymentModel.id_user")
