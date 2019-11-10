from say.models.activity_model import ActivityModel
from . import *
"""
Activity APIs
"""


class GetActivityById(Resource):
    @swag_from("./docs/activity/id.yml")
    def get(self, activity_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}),
                             503)

        try:
            activity = session.query(ActivityModel).filter_by(
                id=activity_id).first()

            if not activity:
                resp = make_response(
                    jsonify({"message": "there is no activity!"}), 200)
                session.close()
                return resp

            resp = make_response(jsonify(obj_to_dict(activity)), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is wrong!"}),
                                 500)

        finally:
            session.close()
            return resp


class GetActivityBySocialWorker(Resource):
    @swag_from("./docs/activity/social_worker.yml")
    def get(self, social_worker_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}),
                             503)

        try:
            activities = (session.query(ActivityModel).filter_by(
                id_social_worker=social_worker_id).all())

            if not activities:
                resp = make_response(
                    jsonify({"message": "there is no activity!"}), 200)
                session.close()
                return resp

            result = {}
            for activity in activities:
                res = {
                    "Id": activity.id,
                    "ActivityCode": activity.activityCode
                }

                result[str(activity.id)] = res

            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is wrong!"}),
                                 500)

        finally:
            session.close()
            return resp


class GetActivityByType(Resource):
    @swag_from("./docs/activity/type.yml")
    def get(self, activity_code):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}),
                             503)

        try:
            activities = (session.query(ActivityModel).filter_by(
                activityCode=activity_code).all())

            if not activities:
                resp = make_response(
                    jsonify({"message": "there is no activity!"}), 200)
                session.close()
                return resp

            result = {}
            for activity in activities:
                res = {
                    "Id": activity.id,
                    "Id_social_worker": activity.id_social_worker
                }

                result[str(activity.id)] = res

            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is wrong!"}),
                                 500)

        finally:
            session.close()
            return resp


class GetAllActivities(Resource):
    @swag_from("./docs/activity/all.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}),
                             503)

        try:
            activities = session.query(ActivityModel).all()

            if not activities:
                resp = make_response(
                    jsonify({"message": "there is no activity!"}), 200)
                session.close()
                return resp

            result = []
            for activity in activities:
                result.append(obj_to_dict(activity))

            resp = make_response(jsonify(result), 200)
            resp.headers["Access-Control-Allow-Origin"] = "*"

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is wrong!"}),
                                 500)

        finally:
            session.close()
            return resp


class AddActivity(Resource):
    @swag_from("./docs/activity/add.yml")
    def post(self, social_worker_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}),
                             503)

        try:
            id_social_worker = social_worker_id
            activity_code = int(request.form["activityCode"])

            new_activity = ActivityModel(id_social_worker=id_social_worker,
                                         activityCode=activity_code)

            session.add(new_activity)
            session.commit()

            resp = make_response(jsonify({"message": "new activity added!"}),
                                 200)
            resp.headers["Access-Control-Allow-Origin"] = "*"

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is wrong!"}),
                                 500)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetActivityById, "/api/v2/activity/activityId=<activity_id>")
api.add_resource(GetActivityBySocialWorker,
                 "/api/v2/activity/socialWorker=<social_worker_id>")
api.add_resource(GetActivityByType, "/api/v2/activity/type=<activity_code>")
api.add_resource(GetAllActivities, "/api/v2/activity/all")
api.add_resource(AddActivity,
                 "/api/v2/activity/add/socialWorker=<social_worker_id>")
