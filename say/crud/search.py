import itertools
import random

from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.functions import count

from say.config import configs
from say.exceptions import HTTPException
from say.models import Child
from say.models import Family
from say.models import Need
from say.models import UserFamily
from say.models.search import Search
from say.models.search import SearchType
from say.models.search import generate_token

from ..models import Invitation
from ..orm import session
from ..schema.search import SearchSchema
from .user import get_say_id


def create_v2(family_id, type_: SearchType):
    say_id = get_say_id()

    invitation = session.query(Invitation).filter(
        Invitation.family_id == family_id,
        Invitation.role.is_(None),
        Invitation.inviter_id == say_id,
    ).one_or_none()

    if not invitation:
        invitation = Invitation(
            inviter_id=say_id,
            family_id=family_id,
        )
        session.add(invitation)
        session.flush()

    search = dict(
        token=invitation.token,
        type_=type_.value,
    )
    return search


def create_v3(child: Child, user_id, type):
    token = generate_token()
    while True:
        token_exists = bool(
            session.query(Search.id).filter(Search.token == token).one_or_none()
        )
        if not token_exists:
            break
        token = generate_token()

    search = Search(child=child, user_id=user_id, type=type, token=token)
    session.add(search)
    return SearchSchema.from_orm(search)


def select_random_child(user_id):
    random_child = None
    excluded = []
    user_children_ids_tuple = (
        session.query(Child.id)
        .join(Family)
        .join(UserFamily)
        .filter(UserFamily.id_user == user_id)
        .filter(UserFamily.isDeleted.is_(False))
    )

    # Flating a nested list like [(1,), (2,)] to [1, 2]
    user_children_ids = list(itertools.chain.from_iterable(user_children_ids_tuple))

    while True:
        child_family_counts = addoptable_child_family_counts_query(
            set([*user_children_ids, *excluded]),
        )

        if child_family_counts.count() == 0:
            raise HTTPException(
                499,
                'Our database is not big as your heart T_T',
            )

        # weight is 1/(1 + family_count ^ FACTOR)
        weights = [
            1 / (1 + x[1]) ** configs.RANDOM_SEARCH_FACTOR for x in child_family_counts
        ]
        addoptable_children = [x[0] for x in child_family_counts]
        selected_child_id = random.choices(addoptable_children, weights)[0]
        random_child: Child = session.query(Child).get(selected_child_id)

        if not random_child.family.is_previous_role_is_taken(user_id):
            break

        excluded.append(random_child.id)

    return random_child


def addoptable_child_family_counts_query(excluded):
    return (
        session.query(Child.id, Family.members_count)
        .join(Need)
        .join(Family)
        .filter(
            Child.isConfirmed.is_(True),
            Child.isDeleted.is_(False),
            Child.isMigrated.is_(False),
            Child.existence_status == 1,
            Child.id.notin_(excluded),
            Need.isConfirmed.is_(True),
            Need.isDeleted.is_(False),
            Need.isDone.is_(False),
        )
    )
