from . import *

"""
Family Model
"""


class FamilyModel(base):
    __tablename__ = "family"

    id = Column(Integer, nullable=False, primary_key=True)
    id_child = Column(Integer, ForeignKey('child.id'), nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)

    child = relationship(
        "ChildModel",
        foreign_keys=id_child,
        back_populates="families",
        uselist=False,
    )
    members = relationship(
        'UserFamilyModel',
        back_populates='family',
    )

    def current_members(self):
        for member in self.members:
            if member.isDeleted:
                continue
            yield member
