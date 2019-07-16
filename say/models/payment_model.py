from say.models.need_model import NeedModel
from say.models.user_model import UserModel
from . import *

"""
Payment Model
"""


class PaymentModel(base):
    __tablename__ = 'payment'

    Id = Column(Integer, nullable=False, primary_key=True)
    Id_need = Column(Integer, ForeignKey(NeedModel.Id), nullable=False)
    Id_user = Column(Integer, ForeignKey(UserModel.Id), nullable=False)
    Amount = Column(Integer, nullable=False)
    CreatedAt = Column(Date, nullable=False)

    need_relation = relationship('NeedModel', foreign_keys='PaymentModel.Id_need')
    user_relation = relationship('UserModel', foreign_keys='PaymentModel.Id_user')
