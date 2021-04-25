from flasgger import swag_from
from flask_restful import Resource
from sqlalchemy.orm import Bundle

from say.api.ext import api
from say.authorization import authorize, get_user_id, get_user_role
from say.decorators import json
from say.models import obj_to_dict, Child, Family, UserFamily
from say.models.user_model import User
from say.orm import session
from say.schema.dashboard import DashboardSchema
from say.exceptions import HTTP_NOT_FOUND


'''
Dashboard API
'''

dashboard_user_fields = (
    'id',
    'userName',
    'firstName',
    'lastName',
)

dashboard_child_fields = (
    'id',
    'avatarUrl',
    'sayName',
    'done_needs_count',
    'spent_credit',
)


class DashboardDataFeed(Resource):
    @authorize
    @json
    @swag_from('./docs/dashboard/feed.yml')
    def get(self):
        user_id = get_user_id()

        user = session.query(
            *[getattr(User, c) for c in dashboard_user_fields]
        ).filter(User.id==user_id).one_or_none()

        if user is None:
            raise HTTP_NOT_FOUND()

        user_dict = dict(zip(dashboard_user_fields, user))

        # id, avatarUrl, sayName, done_needs_count, spent_credit
        children = session.query(
            *[getattr(Child, c) for c in dashboard_child_fields]
        ) \
            .join(Family, Family.id_child == Child.id) \
            .join(UserFamily, UserFamily.id_family == Family.id) \
            .filter(
                UserFamily.id_user == user_id,
                UserFamily.isDeleted == False,
            ) \
            .order_by(UserFamily.created) \

        children_dict = [dict(zip(dashboard_child_fields, child)) for child in children]

        result = DashboardSchema(
            user=user_dict,
            children=children_dict
        )
        return obj_to_dict(result)


api.add_resource(DashboardDataFeed, '/api/v2/dashboard')
