from say.models.child_model import ChildModel
from . import *

"""
Family Model
"""


class FamilyModel(base):
    __tablename__ = 'family'

    Id = Column(Integer, nullable=False, primary_key=True)
    Id_child = Column(Integer,ForeignKey(ChildModel.Id), nullable=False)
    IsDeleted = Column(Boolean, nullable=False, default=False)

    family_child_relation = relationship('ChildModel', foreign_keys='FamilyModel.Id_child')
