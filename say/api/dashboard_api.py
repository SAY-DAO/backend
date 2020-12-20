from flasgger import swag_from
from flask_restful import Resource

from say.api.ext import api
from say.authorization import authorize, get_user_id, get_user_role
from say.decorators import json
from say.models import obj_to_dict, Child, Family, UserFamily
from say.models.user_model import User
from say.orm import session
from say.roles import USER

'''
Dashboard API
'''


class DashboardDataFeed(Resource):
    @authorize
    @json
    @swag_from('./docs/dashboard/feed.yml')
    def get(self):
        user_id = get_user_id()

        user = session.query(User).get(user_id)

        children = session.query(Child)\
            .join(Family, Family.id_child == Child.id) \
            .join(UserFamily, UserFamily.id_family == Family.id) \
            .filter(
                UserFamily.id_user == user_id,
                UserFamily.isDeleted == False,
            ) \
            .order_by(UserFamily.created)

        children_dict = []

        for child in children:
            if not child.isConfirmed and get_user_role() in [USER]:
                continue

            child_dict = obj_to_dict(child)
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

            children_dict.append(child_dict)

        result = dict(
            user=obj_to_dict(user),
            children=children_dict,
        )
        return result


api.add_resource(DashboardDataFeed, '/api/v2/dashboard')
