import itertools

from flasgger import swag_from
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Resource
from flask_restful import abort
from sqlalchemy import func

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

        user_children_ids_tuple = session.query(Child.id) \
            .join(Family) \
            .join(UserFamily) \
            .filter(UserFamily.id_user == user_id) \
            .filter(UserFamily.isDeleted.is_(False))

        # Flating a nested list like [(1,), (2,)] to [1, 2]
        user_children_ids = list(
            itertools.chain.from_iterable(user_children_ids_tuple)
        )

        random_child = Child.get_actives() \
            .filter(Child.id.notin_(user_children_ids)) \
            .filter(Need.isDone == False) \
            .order_by(func.random()) \
            .limit(1) \
            .first()

        if random_child is None:
            return dict(
                message='Unfortunately our database is not big as your heart T_T'
            ), 499

        return crud.search.create(
            family_id=random_child.family.id, type_='random',
        )


class GetSayBrainSearchResult(Resource):
    @authorize
    @swag_from('./docs/search/brain.yml')
    def get(self):
        raise NotImplementedError


api.add_resource(GetRandomSearchResult,
                 '/api/v2/search/random')
api.add_resource(GetSayBrainSearchResult,
                 '/api/v2/search/saybrain')
