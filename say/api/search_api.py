import itertools
from random import randrange

from . import *
from say.api.child_api import get_child_by_id
from say.models.child_model import ChildModel
from say.models.child_need_model import ChildNeedModel
from say.models.need_model import NeedModel
from say.models.family_model import FamilyModel
from say.models.user_family_model import UserFamilyModel
from say.models.user_model import UserModel
"""
Search APIs
"""


class GetRandomSearchResult(Resource):
    @swag_from("./docs/search/random.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}),
                             503)

        try:
            user_children_ids_tuple = session.query(ChildModel.id) \
                .join(FamilyModel) \
                .join(UserFamilyModel) \
                .filter(UserFamilyModel.id_user==user_id) \
                .filter(UserFamilyModel.isDeleted==False) \
                .all()

            # Flating a nested list like [(1,), (2,)] to [1, 2]
            user_children_ids = list(
                itertools.chain.from_iterable(user_children_ids_tuple)
            )

            random_child = session.query(ChildModel) \
                .filter(ChildModel.id.notin_(user_children_ids)) \
                .filter_by(isConfirmed=True) \
                .filter_by(isDeleted=False) \
                .filter_by(isMigrated=False) \
                .join(NeedModel) \
                .filter(NeedModel.status < 2) \
                .filter(NeedModel.isConfirmed==True) \
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
            child_family_member = []
            for member in random_child.families[0].members:
                child_family_member.append(dict(
                    role=member.userRole,
                    firstName=member.user.firstName,
                    lastName=member.user.lastName,
                ))

            child_dict["childFamilyMembers"] = child_family_member
            child_dict["familyId"] = random_child.families[0].id

            resp = jsonify(child_dict)
            return resp

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetSayBrainSearchResult(Resource):
    @swag_from("./docs/search/brain.yml")
    def get(self, user_id):
        return make_response(jsonify({"message": "not implemented yet!"}), 501)


"""
API URLs
"""

api.add_resource(GetRandomSearchResult,
                 "/api/v2/search/random/userId=<user_id>")
api.add_resource(GetSayBrainSearchResult,
                 "/api/v2/search/sayBrain/userId=<user_id>")
