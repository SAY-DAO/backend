import itertools
import random

from flasgger import swag_from
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Resource
from flask_restful import abort
from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.functions import count

from say.config import configs
from say.models import commit
from say.models.child_model import Child
from say.models.family_model import Family
from say.models.need_model import Need
from say.models.user_family_model import UserFamily

from .. import crud
from ..authorization import authorize
from ..authorization import get_user_id
from ..decorators import json
from ..orm import session
from .ext import api
from .ext import logger


'''
Search APIs
'''


class GetRandomSearchResult(Resource):
    @json
    @commit
    @swag_from('./docs/search/random.yml')
    def post(self):
        try:
            user_id = get_user_id()
        except NoAuthorizationError:
            logger.info('random search: public')
            user_id = None

        except Exception as e:
            # Any other error
            logger.info('random search: bad jwt')
            logger.info(str(e))
            abort(403)

        user_children_ids_tuple = (
            session.query(Child.id)
            .join(Family)
            .join(UserFamily)
            .filter(UserFamily.id_user == user_id)
            .filter(UserFamily.isDeleted.is_(False))
        )

        # Flating a nested list like [(1,), (2,)] to [1, 2]
        user_children_ids = list(itertools.chain.from_iterable(user_children_ids_tuple))
        child_family_counts = (
            session.query(Child.id, count(distinct(UserFamily.id_user)))
            .filter(Child.isConfirmed.is_(True))
            .filter(Child.isDeleted.is_(False))
            .filter(Child.isMigrated.is_(False))
            .filter(Child.existence_status == 1)
            .join(Need)
            .filter(Need.isConfirmed.is_(True))
            .filter(Need.isDeleted.is_(False))
            .join(Family)
            .join(UserFamily)
            .filter(Child.id.notin_(user_children_ids))
            .filter(UserFamily.isDeleted.is_(False))
            .filter(Need.isDone.is_(False))
            .group_by(Child.id, UserFamily.id_family)
        )

        if child_family_counts.count() == 0:
            return (
                dict(message='Unfortunately our database is not big as your heart T_T'),
                499,
            )

        # weight is 1/(1 + family_count ^ FACTOR)
        weights = [
            1 / (1 + x[1]) ** configs.RANDOM_SEARCH_FACTOR for x in child_family_counts
        ]
        addoptable_children = [x[0] for x in child_family_counts]
        selected_child_id = random.choices(addoptable_children, weights)[0]
        random_child: Child = session.query(Child).get(selected_child_id)

        return crud.search.create(
            family_id=random_child.family.id,
            type_='random',
        )


class GetSayBrainSearchResult(Resource):
    @authorize
    @swag_from('./docs/search/brain.yml')
    def get(self):
        raise NotImplementedError


api.add_resource(GetRandomSearchResult, '/api/v2/search/random')
api.add_resource(GetSayBrainSearchResult, '/api/v2/search/saybrain')
