from say.api.need_api import get_all_urgent_needs
from say.api.user_api import get_user_by_something
from . import *

"""
Dashboard API
"""


class DashboardDataFeed(Resource):
    @swag_from('./apidocs/dashboard/feed.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            data = get_user_by_something(session, user_id)
            needs = get_all_urgent_needs(session)

            data['GlobalUrgentNeeds'] = needs

            resp = Response(json.dumps(data))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'ERROR OCCURRED!'}))

        finally:
            session.close()
            return resp


"""
API URLs 
"""

api.add_resource(DashboardDataFeed, '/api/v2/dashboard/userId=<user_id>')
