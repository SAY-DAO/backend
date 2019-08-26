from random import randrange

from say.api.child_api import get_child_by_id
from say.models.child_model import ChildModel
from say.models.child_need_model import ChildNeedModel
from say.models.family_model import FamilyModel
from say.models.user_family_model import UserFamilyModel
from say.models.user_model import UserModel
from . import *

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
    @swag_from('./docs/search/random.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = Response(json.dumps({'message': 'major error occurred!'}), status=500)

        try:
            other_families = session.query(UserFamilyModel).filter(UserFamilyModel.id_user != user_id).filter_by(
                isDeleted=False).all()
            other_children = [family.family_relation.id_child for family in other_families]

            children = session.query(ChildModel).filter(
                or_(ChildModel.id.in_(other_children), ChildModel.sayFamilyCount == 0)).filter_by(
                isDeleted=False).filter_by(isMigrated=False).all()

            search_data, index = [], []
            for child in children:
                if not child.isConfirmed:
                    continue

                needs = session.query(ChildNeedModel).filter_by(id_child=child.id).filter_by(isDeleted=False).all()
                need_amount = len(needs)

                family = session.query(FamilyModel).filter_by(isDeleted=False).filter_by(id_child=child.id).first()
                members = session.query(UserFamilyModel).filter_by(id_family=family.id).filter_by(isDeleted=False).all()

                family_res = '{'
                for member in members:
                    user = session.query(UserModel).filter_by(isDeleted=False).filter_by(id=member.id_user).first()
                    user_data = obj_to_dict(user)
                    user_data['Role'] = member.userRole
                    family_res += f'"{str(user.id)}": {utf8_response(user_data)}, '

                child_family = family_res[:-2] + '}' if len(family_res) != 1 else '{}'

                child_data = get_child_by_id(session, child.id)
                child_data = child_data[:-1] + f', "ChildFamily": {child_family}{"}"}'

                index.append(3 * need_amount - 2 * child.sayFamilyCount)
                search_data.append(child_data)

            search_data_temp = index.copy()
            search_data_temp.sort(reverse=True)
            out = [search_data[index.index(i)] for i in search_data_temp]
            list_bias(search_data_temp)

            search_range = sum(search_data_temp)
            r = randrange(search_range + 1)
            for i in range(len(search_data_temp)):
                if r <= sum(search_data_temp[:i + 1]):
                    resp = Response(out[i])
                    break

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetSayBrainSearchResult(Resource):
    @swag_from('./docs/search/brain.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = Response(json.dumps({'message': 'major error occurred!'}), status=500)

        try:
            other_families = session.query(UserFamilyModel).filter(UserFamilyModel.id_user != user_id).filter_by(
                isDeleted=False).all()
            other_children = [family.family_relation.id_child for family in other_families]

            children = session.query(ChildModel).filter(
                or_(ChildModel.id.in_(other_children), ChildModel.sayFamilyCount == 0)).filter_by(
                isDeleted=False).filter_by(isMigrated=False).all()

            search_data, index = [], []
            for child in children:
                if not child.isConfirmed:
                    continue

                needs = session.query(ChildNeedModel).filter_by(id_child=child.id).filter_by(isDeleted=False).all()
                need_amount = len(needs)

                family = session.query(FamilyModel).filter_by(isDeleted=False).filter_by(id_child=child.id).first()
                members = session.query(UserFamilyModel).filter_by(id_family=family.id).filter_by(isDeleted=False).all()

                family_res = '{'
                for member in members:
                    user = session.query(UserModel).filter_by(isDeleted=False).filter_by(id=member.id_user).first()
                    user_data = obj_to_dict(user)
                    user_data['Role'] = member.userRole
                    family_res += f'"{str(user.id)}": {utf8_response(user_data)}, '

                child_family = family_res[:-2] + '}' if len(family_res) != 1 else '{}'

                child_data = get_child_by_id(session, child.id)
                child_data = child_data[:-1] + f', "ChildFamily": {child_family}{"}"}'

                index.append(3 * need_amount - 2 * child.sayFamilyCount)
                search_data.append(child_data)

            search_data_temp = index.copy()
            search_data_temp.sort(reverse=True)
            out = [search_data[index.index(i)] for i in search_data_temp]
            list_bias(search_data_temp)

            search_range = sum(search_data_temp)
            r = randrange(search_range + 1)
            for i in range(len(search_data_temp)):
                if r <= sum(search_data_temp[:i + 1]):
                    resp = Response(out[i])
                    break

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetRandomSearchResult, '/api/v2/search/random/userId=<user_id>')
api.add_resource(GetSayBrainSearchResult, '/api/v2/search/sayBrain/userId=<user_id>')
