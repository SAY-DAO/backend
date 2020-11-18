from . import *

"""
Family Model
"""


class Family(base, Timestamp):
    __tablename__ = "family"

    id = Column(Integer, nullable=False, primary_key=True)
    id_child = Column(
        Integer, 
        ForeignKey('child.id'), 
        nullable=False, 
        unique=True,
    )
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

    invitations = relationship(
        'Invitation',
        back_populates='family',
    )

    def current_members(self):
        for member in self.members:
            if member.isDeleted:
                continue
            yield member

    def is_in_family(self, user):
        for member in self.members:
            if member.id_user == user.id and not member.isDeleted:
                return False
        return True

    def can_join(self, user, role):
        for member in self.members:
            # Child has father (xor mother)
            if role in (0, 1) and member.userRole == role \
                    and not member.isDeleted:
                return False

        return True

