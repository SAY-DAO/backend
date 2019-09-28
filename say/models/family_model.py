from say.models.child_model import ChildModel
from . import *

"""
Family Model
"""


class FamilyModel(base):
    __tablename__ = "family"

    id = Column(Integer, nullable=False, primary_key=True)
    id_child = Column(Integer, ForeignKey(ChildModel.id), nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)

    family_child_relation = relationship(
        "ChildModel", foreign_keys="FamilyModel.id_child"
    )
