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
        resp = {"message": "major error occurred!"}

        try:
            activity = session.query(ActivityModel).filter_by(id=activity_id).first()

            if not activity:
                resp = Response(json.dumps({"message": "there is no activity!"}))
                session.close()
                return resp

            resp = Response(utf8_response(obj_to_dict(activity)), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "something is wrong!"}, status=500))

        finally:
            session.close()
            return resp


class GetActivityBySocialWorker(Resource):
    @swag_from("./docs/activity/social_worker.yml")
    def get(self, social_worker_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            activities = (
                session.query(ActivityModel)
                .filter_by(id_social_worker=social_worker_id)
                .all()
            )

            if not activities:
                resp = Response(json.dumps({"message": "there is no activity!"}))
                session.close()
                return resp

            result = {}
            for activity in activities:
                res = {"Id": activity.id, "ActivityCode": activity.activityCode}

                result[str(activity.id)] = res

            resp = Response(utf8_response(result, True), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "something is wrong!"}, status=500))

        finally:
            session.close()
            return resp


class GetActivityByType(Resource):
    @swag_from("./docs/activity/type.yml")
    def get(self, activity_code):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            activities = (
                session.query(ActivityModel).filter_by(activityCode=activity_code).all()
            )

            if not activities:
                resp = Response(json.dumps({"message": "there is no activity!"}))
                session.close()
                return resp

            result = {}
            for activity in activities:
                res = {"Id": activity.id, "Id_social_worker": activity.id_social_worker}

                result[str(activity.id)] = res

            resp = Response(utf8_response(result, True), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "something is wrong!"}, status=500))

        finally:
            session.close()
            return resp


class GetAllActivities(Resource):
    @swag_from("./docs/activity/all.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            activities = session.query(ActivityModel).all()

            if not activities:
                resp = Response(json.dumps({"message": "there is no activity!"}))
                session.close()
                return resp

            result = {}
            for activity in activities:
                res = {
                    "Id": activity.id,
                    "Id_social_worker": activity.id_social_worker,
                    "ActivityCode": activity.activityCode,
                }

                result[str(activity.id)] = res

            resp = Response(
                utf8_response(result, True),
                status=200,
                headers={"Access-Control-Allow-Origin": "*"},
            )

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "something is wrong!"}), status=500)

        finally:
            session.close()
            return resp


class AddActivity(Resource):
    @swag_from("./docs/activity/add.yml")
    def post(self, social_worker_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            id_social_worker = social_worker_id
            activity_code = int(request.form["activityCode"])

            new_activity = ActivityModel(
                id_social_worker=id_social_worker, activityCode=activity_code
            )

            session.add(new_activity)
            session.commit()

            resp = Response(
                json.dumps({"message": "new activity added!"}),
                status=200,
                headers={"Access-Control-Allow-Origin": "*"},
            )

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "something is wrong!"}), status=500)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetActivityById, "/api/v2/activity/activityId=<activity_id>")
api.add_resource(
    GetActivityBySocialWorker, "/api/v2/activity/socialWorker=<social_worker_id>"
)
api.add_resource(GetActivityByType, "/api/v2/activity/type=<activity_code>")
api.add_resource(GetAllActivities, "/api/v2/activity/all")
api.add_resource(AddActivity, "/api/v2/activity/add/socialWorker=<social_worker_id>")
