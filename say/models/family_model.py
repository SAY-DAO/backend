from sqlalchemy.orm import column_property

from . import *
from .user_family_model import UserFamily


"""
Family Model
"""


class Family(base, Timestamp):
    __tablename__ = "family"
    __versioned__ = {}

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

    current_members = relationship(
        'UserFamily',
        back_populates='family',
        primaryjoin='''and_(
            Family.id==UserFamily.id_family,
            UserFamily.is_deleted.is_(False),
        )''',
    )

    invitations = relationship(
        'Invitation',
        back_populates='family',
    )

    members_count = column_property(
        select(
            [
                coalesce(
                    func.count(UserFamily.id_user),
                    0,
                )
            ]
        )
        .where(
            and_(
                UserFamily.is_deleted.is_(False),
                UserFamily.id_family == id,
            )
        )
        .correlate_except(UserFamily)
        .scalar_subquery(),
    )

    # def current_members(self):
    #     for member in self.members:
    #         if member.isDeleted:
    #             continue
    #         yield member

    def is_in_family(self, user):
        for member in self.members:
            if member.id_user == user.id and not member.isDeleted:
                return False
        return True

    def can_join(self, role):
        for member in self.members:
            # Child has father (xor mother)
            if role in (0, 1) and member.userRole == role and not member.isDeleted:
                return False

        return True

    def is_previous_role_is_taken(self, user_id):
        if user_id is None:
            return False

        previous_role = None
        for member in self.members:
            if member.id_user == user_id:
                previous_role = member.role
                break

        if previous_role is None or previous_role not in (0, 1):
            # User is new member or was not father or mother
            return False

        for member in self.members:
            if member.role == previous_role and member.isDeleted is False:
                return True

        return False
