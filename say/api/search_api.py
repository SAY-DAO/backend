import itertools
from random import randrange

from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import abort
from sqlalchemy import func

from . import *
from say.models import session, obj_to_dict, commit
from say.models.child_model import Child
from say.models.child_need_model import ChildNeed
from say.models.need_model import Need
from say.models.family_model import Family
from say.models.user_family_model import UserFamily
from say.models.user_model import User
from .. import crud

"""
Search APIs
"""


class GetRandomSearchResult(Resource):

    @json
    @commit
    @swag_from("./docs/search/random.yml")
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
            family_id=random_child.family.id, user_id=user_id, type_='random',
        )


class GetSayBrainSearchResult(Resource):
    @authorize
    @swag_from("./docs/search/brain.yml")
    def get(self):
        return make_response(jsonify({"message": "not implemented yet!"}), 501)


"""
API URLs
"""

api.add_resource(GetRandomSearchResult,
                 "/v2/search/random")
api.add_resource(GetSayBrainSearchResult,
                 "/v2/search/saybrain")
