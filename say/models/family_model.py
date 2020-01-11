from . import *

"""
Family Model
"""


class Family(base, Timestamp):
    __tablename__ = "family"

    id = Column(Integer, nullable=False, primary_key=True)
    id_child = Column(Integer, ForeignKey('child.id'), nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)

    child = relationship(
        "Child",
        foreign_keys=id_child,
        back_populates="family",
        uselist=False,
    )
    members = relationship(
        'UserFamily',
        back_populates='family',
    )

    def current_members(self):
        for member in self.members:
            if member.isDeleted:
                continue
            yield member
