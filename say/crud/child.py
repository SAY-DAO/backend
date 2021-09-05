from sqlalchemy.orm import selectinload

from say.models import Child
from say.models import Family
from say.models import User
from say.models import UserFamily
from say.orm import obj_to_dict
from say.orm import session
from say.schema.child import FamilyMemberSchema
from say.schema.child import UserChildSchema


def is_gone(id_):
    return (
        session.query(Child.id)
        .filter(
            Child.id == id_,
            Child.existence_status != 1,
        )
        .scalar()
    )


def get_family_members(id, include_deleted=False):
    query = (
        session.query(
            UserFamily.userRole,
            User.userName,
            UserFamily.isDeleted,
            User.id,
            User.avatarUrl,
        )
        .select_from(UserFamily)
        .join(Family, Family.id == UserFamily.id_family)
        .join(User, User.id == UserFamily.id_user)
        .filter(
            Family.id_child == id,
            True if include_deleted else UserFamily.isDeleted.is_(False),
        )
    )

    for member in query:
        yield FamilyMemberSchema(
            role=member[0],
            username=member[1],
            isDeleted=member[2],
            member_id=member[3],
            avatarUrl=member[4],
        )


def child_by_id(id):
    child = (
        session.query(Child)
        .filter(Child.isDeleted.is_(False))
        .filter(Child.id == id)
        .options(selectinload('family.members.user'))
        .one_or_none()
    )

    if child is None:
        return

    child_dict = obj_to_dict(child)
    child_family_members = [
        x for x in child.get_family_members(child.id, include_deleted=True)
    ]

    return UserChildSchema(**child_dict, childFamilyMembers=child_family_members)
