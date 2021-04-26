from say.models import Child
from say.models import Family
from say.models import User
from say.models import UserFamily
from say.orm import session
from say.schema.child import FamilyMemberSchema


def is_gone(id_):
    return session.query(Child.id).filter(
        Child.id == id_,
        Child.existence_status != 1,
    ).scalar()


def get_family_members(id):
    query = session.query(
        UserFamily.userRole,
        User.userName,
        UserFamily.isDeleted,
        User.id,
    ) \
        .select_from(UserFamily) \
        .join(Family, Family.id == UserFamily.id_family) \
        .join(User, User.id == UserFamily.id_user) \
        .filter(
            Family.id_child == id,
            UserFamily.isDeleted.is_(False),    
        )

    for member in query:
        yield FamilyMemberSchema(
            role=member[0],
            username=member[1],
            isDeleted=member[2],
            member_id=member[3],
        )
