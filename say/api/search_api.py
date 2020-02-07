import itertools
from random import randrange

from sqlalchemy import func

from . import *
from say.models import session, obj_to_dict
from say.models.child_model import Child
from say.models.child_need_model import ChildNeed
from say.models.need_model import Need
from say.models.family_model import Family
from say.models.user_family_model import UserFamily
from say.models.user_model import User
"""
Search APIs
"""


class GetRandomSearchResult(Resource):
    @authorize
    @swag_from("./docs/search/random.yml")
    def get(self):
        user_id = get_user_id()
        resp = make_response(jsonify({"message": "major error occurred!"}),
                             503)

        try:
            user_children_ids_tuple = session.query(Child.id) \
                .join(Family) \
                .join(UserFamily) \
                .filter(UserFamily.id_user==user_id) \
                .filter(UserFamily.isDeleted==False) \
                .all()

            # Flating a nested list like [(1,), (2,)] to [1, 2]
            user_children_ids = list(
                itertools.chain.from_iterable(user_children_ids_tuple)
            )

            random_child = session.query(Child) \
                .filter(Child.id.notin_(user_children_ids)) \
                .filter_by(isConfirmed=True) \
                .filter_by(isDeleted=False) \
                .filter_by(isMigrated=False) \
                .join(Need) \
                .filter(Need.isDone==False) \
                .filter(Need.isConfirmed==True) \
                .filter(Need.isDeleted==False) \
                .order_by(func.random()) \
                .limit(1) \
                .first()

            if random_child is None:
                resp = make_response(
                    dict(message='Unfortunately our database is not big as your heart T_T'),
                    499,
                )
                return resp

            child_dict = obj_to_dict(random_child)
            del child_dict['phoneNumber']
            del child_dict['firstName']
            del child_dict['firstName_translations']
            del child_dict['lastName']
            del child_dict['lastName_translations']
            del child_dict['nationality']
            del child_dict['country']
            del child_dict['city']
            del child_dict['birthPlace']
            del child_dict['address']
            del child_dict['id_social_worker']
            del child_dict['id_ngo']

            child_family_member = []
            for member in random_child.family.current_members():
                child_family_member.append(dict(
                    role=member.userRole,
                    firstName=member.user.firstName,
                    lastName=member.user.lastName,
                ))

            child_dict["childFamilyMembers"] = child_family_member
            child_dict["familyId"] = random_child.family.id

            resp = jsonify(child_dict)
            return resp

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetSayBrainSearchResult(Resource):
    @authorize
    @swag_from("./docs/search/brain.yml")
    def get(self):
        return make_response(jsonify({"message": "not implemented yet!"}), 501)


"""
API URLs
"""

api.add_resource(GetRandomSearchResult,
                 "/api/v2/search/random")
api.add_resource(GetSayBrainSearchResult,
                 "/api/v2/search/saybrain")
