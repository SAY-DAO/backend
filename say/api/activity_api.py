from say.models.activity_model import ActivityModel
from . import *

"""
Activity APIs
"""


class GetActivityById(Resource):
    @swag_from('./apidocs/activity/id.yml')
    def get(self, activityId):
        Session = sessionmaker(db)
        session = Session()
        try:
            activity = session.query(ActivityModel).filter_by(Id=activityId).first()

            if not activity:
                resp = Response(json.dumps({'message': 'something is Wrong !!'}))
                session.close()
                return resp
            resp = Response(json.dumps(obj_to_dict(activity)), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'something is Wrong !!'}, status=500))

        finally:
            session.close()
            return resp


class GetActivityBySocialWorker(Resource):
    @swag_from('./apidocs/activity/socialworker.yml')
    def get(self, socialworker_id):
        Session = sessionmaker(db)
        session = Session()
        try:
            activities = session.query(ActivityModel).filter_by(Id_social_worker=socialworker_id).all()
            r = {}
            for a in activities:
                res = {
                    'Id': a.Id,
                    'ActivityCode': a.ActivityCode,
                }
                r[a.Id] = res

            resp = Response(json.dumps(r), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'something is Wrong !!'}, status=500))

        finally:
            session.close()
            return resp


class GetActivityByType(Resource):
    @swag_from('./apidocs/activity/type.yml')
    def get(self, activityCode):
        Session = sessionmaker(db)
        session = Session()
        try:
            activities = session.query(ActivityModel).filter_by(ActivityCode=activityCode).all()
            r = {}
            for a in activities:
                res = {
                    'Id': a.Id,
                    'Id_social_worker': a.Id_social_worker,
                }
                r[a.Id] = res

            resp = Response(json.dumps(r), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'something is Wrong !!'}, status=500))

        finally:
            session.close()
            return resp


class GetAllActivities(Resource):
    @swag_from('./apidocs/activity/all.yml')
    def get(self):
        Session = sessionmaker(db)
        session = Session()
        try:
            activities = session.query(ActivityModel).all()

            r = {}
            for a in activities:
                res = {
                    'Id': a.Id,
                    'Id_social_worker': a.Id_social_worker,
                    'ActivityCode': a.ActivityCode
                }
                r[a.Id] = res

            resp = Response(json.dumps(r), status=200, headers={'Access-Control-Allow-Origin': '*'})
        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'Something is Wrong !!!'}), status=500)
        finally:
            session.close()
            return resp


class AddActivity(Resource):
    @swag_from('./apidocs/activity/add.yml')
    def post(self, socialworker_id):
        Session = sessionmaker(db)
        session = Session()
        try:
            Id_social_worker = socialworker_id
            ActivityCode = int(request.json['ActivityCode'])
            new_activity = ActivityModel(Id_social_worker=Id_social_worker, ActivityCode=ActivityCode)
            session.add(new_activity)
            session.commit()

            res = {'message': 'New Activity is added'}
            resp = Response(json.dumps(res), status=200, headers={'Access-Control-Allow-Origin': '*'})

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'Something is Wrong !!!'}), status=500)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetActivityById, '/api/v2/activity/activityId=<activityId>')
api.add_resource(GetActivityBySocialWorker, '/api/v2/activity/socialWorker=<socialworker_id>')
api.add_resource(GetActivityByType, '/api/v2/activity/type=<activityCode>')
api.add_resource(GetAllActivities, '/api/v2/activity/all')
api.add_resource(AddActivity, '/api/v2/activity/add/socialWorker=<socialworker_id>')
