from sqlalchemy.orm import joinedload

from say.models import session, obj_to_dict
from say.models.user_model import User
from . import *

"""
Dashboard API
"""


class DashboardDataFeed(Resource):
    @authorize
    @swag_from("./docs/dashboard/feed.yml")
    def get(self):
        user_id = get_user_id()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = session.query(User).options(
                joinedload('user_families').joinedload('family').joinedload('child')
            ).get(user_id)

            children = []
            for family_member in user.user_families:
                child = family_member.family.child
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

                children.append(child_dict)

            result = dict(
                user=obj_to_dict(user),
                children=children,
            )
            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": str(e)}), 500)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(DashboardDataFeed, "/api/v2/dashboard")
