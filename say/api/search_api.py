from random import random as r

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
            families = session.query(UserFamilyModel).filter(UserFamilyModel.Id_user != user_id).filter_by(
                IsDeleted=False).all()
            other_children = [family.Id_child for family in families]
            children = session.query(ChildModel).filter(ChildModel.Id.in_(other_children)).filter_by(
                IsDeleted=False).all()

            search_data = []
            for child in children:
                needs = session.query(ChildNeedModel).filter_by(Id_child=child.Id).filter_by(IsDeleted=False).all()
                need_amount = len(needs)

                child_needs = {}
                for need in needs:
                    need_data = obj_to_dict(need)
                    child_needs[need.Id] = need_data

                child_data = obj_to_dict(child)
                child_data['Needs'] = child_needs

                search_data.append([3 * need_amount - 2 * child.SayFamilyCount, child])

            search_data.sort(reverse=True)
            search_data = [data[1] for data in search_data]

            res = []
            for data in search_data:
                if r() > 0.7:
                    res.append(data)

            resp = Response(json.dumps(res))

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
            families = session.query(UserFamilyModel).filter(UserFamilyModel.Id_user != user_id).filter_by(
                IsDeleted=False).all()
            other_children = [family.Id_child for family in families]
            children = session.query(ChildModel).filter(ChildModel.Id.in_(other_children)).filter_by(
                IsDeleted=False).all()

            search_data = []
            for child in children:
                needs = session.query(ChildNeedModel).filter_by(Id_child=child.Id).filter_by(IsDeleted=False).all()
                need_amount = len(needs)

                child_needs = {}
                for need in needs:
                    need_data = obj_to_dict(need)
                    child_needs[need.Id] = need_data

                child_data = obj_to_dict(child)
                child_data['Needs'] = child_needs

                search_data.append([3 * need_amount - 2 * child.SayFamilyCount, child])

            search_data.sort(reverse=True)
            search_data = [data[1] for data in search_data]

            res = []
            for data in search_data:
                if r() > 0.7:
                    res.append(data)

            resp = Response(json.dumps(res))

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
