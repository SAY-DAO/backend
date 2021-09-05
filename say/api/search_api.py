
from flasgger import swag_from
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Resource
from flask_restful import abort

from say.crud.search import select_random_child
from say.models import commit
from say.models.search import SearchType

from .. import crud
from ..authorization import authorize
from ..authorization import get_user_id
from ..decorators import json
from .ext import api
from .ext import logger


'''
Search APIs
'''


def user_id_from_header():
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

    return user_id


class GetRandomSearchV2(Resource):
    @json
    @commit
    @swag_from('./docs/search/random-v2.yml')
    def post(self):
        user_id = user_id_from_header()
        random_child = select_random_child(user_id)
        return crud.search.create_v2(
            family_id=random_child.family.id,
            type_=SearchType.random,
        )


class GetRandomSearchV3(Resource):
    @json
    @commit
    @swag_from('./docs/search/random-v3.yml')
    def post(self):
        user_id = user_id_from_header()
        random_child = select_random_child(user_id)
        return crud.search.create_v3(
            user_id=user_id,
            child=random_child,
            type=SearchType.random,
        )


class GetSayBrainSearchResult(Resource):
    @authorize
    @swag_from('./docs/search/brain.yml')
    def get(self):
        raise NotImplementedError


api.add_resource(GetRandomSearchV3, '/api/v3/search/random')
api.add_resource(GetRandomSearchV2, '/api/v2/search/random')
api.add_resource(GetSayBrainSearchResult, '/api/v2/search/saybrain')
