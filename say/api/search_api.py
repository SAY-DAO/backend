from random import randrange

from . import *
from say.api.child_api import get_child_by_id
from say.models.child_model import ChildModel
from say.models.child_need_model import ChildNeedModel
from say.models.family_model import FamilyModel
from say.models.user_family_model import UserFamilyModel
from say.models.user_model import UserModel


"""
Search APIs
"""


def list_bias(array: list):
    # array is a sorted list:  5, 4, 3,...
    base = array[-1]
    if base <= 0:
        bias = abs(base) + 1
    else:
        return

    for a in range(len(array)):
        array[a] += bias

    return


class GetRandomSearchResult(Resource):
    @swag_from("./docs/search/random.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            children = (
                session.query(ChildModel)
                .filter_by(isConfirmed=True)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
            )
            debug(f'result chidren --> {children}')

            user_id = int(user_id)
            user = session.query(UserModel).get(user_id)

            search_data, index = [], []
            for child in children:
                for family in child.families:
                    if user in family.users:
                        continue

                    needs = (
                        session.query(ChildNeedModel)
                        .filter_by(id_child=child.id)
                        .filter_by(isDeleted=False)
                        .all()
                    )
                    need_amount = len(needs)

                    family = (
                        session.query(FamilyModel)
                        .filter_by(isDeleted=False)
                        .filter_by(id_child=child.id)
                        .first()
                    )
                    members = (
                        session.query(UserFamilyModel)
                        .filter_by(id_family=family.id)
                        .filter_by(isDeleted=False)
                        .all()
                    )

                    family_res = {}
                    for member in members:
                        user = (
                            session.query(UserModel)
                            .filter_by(isDeleted=False)
                            .filter_by(id=member.id_user)
                            .first()
                        )
                        user_data = obj_to_dict(user)
                        user_data["Role"] = member.userRole
                        family_res[str(user.id)] = user_data

                    child_data = get_child_by_id(session, child.id)
                    child_data["ChildFamily"] = family_res
                    child_data["FamilyId"] = family.id

                    index.append(3 * need_amount - 2 * child.sayFamilyCount)
                    search_data.append(child_data)

            if len(search_data) == 0:
                resp = make_response(dict(message='Unfortunately our database is not big as your heart'), 499)
                return

            search_data_temp = index.copy()
            search_data_temp.sort(reverse=True)
            out = [search_data[index.index(i)] for i in search_data_temp]
            list_bias(search_data_temp)

            search_range = sum(search_data_temp)
            r = randrange(search_range + 1)
            for i in range(len(search_data_temp)):
                if r <= sum(search_data_temp[: i + 1]):
                    resp = make_response(jsonify(out[i]), 200)
                    break

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetSayBrainSearchResult(Resource):
    @swag_from("./docs/search/brain.yml")
    def get(self, user_id):
        return make_response(jsonify({"message": "not implemented yet!"}),
                             501)


"""
API URLs
"""

api.add_resource(GetRandomSearchResult, "/api/v2/search/random/userId=<user_id>")
api.add_resource(GetSayBrainSearchResult, "/api/v2/search/sayBrain/userId=<user_id>")
