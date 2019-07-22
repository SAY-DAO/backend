from random import randrange

from say.models.child_model import ChildModel
from say.models.child_need_model import ChildNeedModel
from say.models.user_family_model import UserFamilyModel
from . import *

"""
Search APIs
"""


class GetRandomSearchResult(Resource):
    @swag_from('./apidocs/search/random.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            other_families = session.query(UserFamilyModel).filter(UserFamilyModel.Id_user != user_id).filter_by(
                IsDeleted=False).all()
            other_children = [family.family_relation.Id_child for family in other_families]

            children = session.query(ChildModel).filter(
                or_(ChildModel.Id.in_(other_children), ChildModel.HasFamily.is_(False))).filter_by(
                IsDeleted=False).all()

            search_data, index = [], []
            for child in children:
                needs = session.query(ChildNeedModel).filter_by(Id_child=child.Id).filter_by(IsDeleted=False).all()
                need_amount = len(needs)

                child_needs = {}
                for need in needs:
                    need_data = obj_to_dict(need)
                    child_needs[need.Id] = need_data

                child_data = obj_to_dict(child)
                child_data['Needs'] = child_needs

                index.append(3 * need_amount - 2 * child.SayFamilyCount)
                search_data.append(child_data)

            search_data_temp = index.copy()
            search_data_temp.sort(reverse=True)
            out = [search_data[index.index(i)] for i in search_data_temp]

            search_range = sum(search_data_temp)
            for j in search_data_temp:
                search_range += 1 if j == 0 else 0

            r = randrange(search_range)
            for i in range(len(search_data_temp)):
                if r <= sum(search_data_temp[:i + 1]):
                    resp = Response(json.dumps(out[i]))
                    break

            print(10)

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetSayBrainSearchResult(Resource):
    @swag_from('./apidocs/search/brain.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            other_families = session.query(UserFamilyModel).filter(UserFamilyModel.Id_user != user_id).filter_by(
                IsDeleted=False).all()
            other_children = [family.family_relation.Id_child for family in other_families]

            children = session.query(ChildModel).filter(
                or_(ChildModel.Id.in_(other_children), ChildModel.HasFamily.is_(False))).filter_by(
                IsDeleted=False).all()

            search_data, index = [], []
            for child in children:
                needs = session.query(ChildNeedModel).filter_by(Id_child=child.Id).filter_by(IsDeleted=False).all()
                need_amount = len(needs)

                child_needs = {}
                for need in needs:
                    need_data = obj_to_dict(need)
                    child_needs[need.Id] = need_data

                child_data = obj_to_dict(child)
                child_data['Needs'] = child_needs

                index.append(3 * need_amount - 2 * child.SayFamilyCount)
                search_data.append(child_data)

            search_data_temp = index.copy()
            search_data_temp.sort(reverse=True)
            out = [search_data[index.index(i)] for i in search_data_temp]

            search_range = sum(search_data_temp)
            for j in search_data_temp:
                search_range += 1 if j == 0 else 0

            r = randrange(search_range)
            for i in range(len(search_data_temp)):
                if r <= sum(search_data_temp[:i + 1]):
                    resp = Response(json.dumps(out[i]))
                    break

            print(10)

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
