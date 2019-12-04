from say.api.need_api import get_all_urgent_needs
from say.api.user_api import get_user_by_id, get_user_needs
from say.models.user_model import UserModel
from . import *

"""
Dashboard API
"""


class DashboardDataFeed(Resource):
    @swag_from("./docs/dashboard/feed.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            user = (
                session.query(UserModel)
                .filter_by(id=user_id)
                .filter_by(isDeleted=False)
                .first()
            )

            data = get_user_by_id(session, user_id)
            needs = get_user_needs(session, user, urgent=True)

            data["UserUrgentNeeds"] = needs

            resp = make_response(jsonify(data), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED!"}), 500)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(DashboardDataFeed, "/api/v2/dashboard/userId=<user_id>")
