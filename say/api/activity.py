from flask import Flask
from flask import Blueprint , Response , request , json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from say.config import db

from say.models import Activity


activity  = Blueprint('activity', __name__)

base = declarative_base()


@activity.route('/activity' , methods = ['GET' , 'POST'])
def api_activity():
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)

    if request.method == 'GET':
        try:
            activities = session.query(Activity)
            
            r = {}
            for a in activities:
                res = {
                    'id' : a.id , 
                    'socialworker_id' : a.socialworker_id,
                    'activityCode' : a.activityCode
                    }
                r[a.id] = res
        
            resp = Response(json.dumps(r) , status= 200)
        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message' : 'Something is Wrong !!!'}) , status= 500)
        finally:
            session.close()
            return resp
 
 
    if request.method == 'POST':
        social_worker_id = request.form['social_worker_id']
        activityCode = request.form['activityCode']

        
        try :   
            new_activity = Activity(socialworker_id = social_worker_id , activityCode = activityCode)
            session.add(new_activity)
            session.commit()

            res = {'message' : 'New Activity is added'}
            resp = Response(json.dumps(res) , status=200)
            
        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message' : 'Something is Wrong !!!'}) , status= 500)

        finally :
            session.close()
            return resp



@activity.route('/activity/type/<int:activityCode>' , methods=['GET'] )
def getActivityByType(activityCode):
    
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)
    try : 
        activities = session.query(Activity).filter_by(activityCode = activityCode)
        r = {}
        for a in activities:
            res = {
                'id' : a.id,
                'socialworker_id' : a.socialworker_id, 
            }
            r[a.id] = res

        resp = Response(json.dumps(r) , status=200)
    
    except Exception as e :
        print(e)
        resp = Response(json.dumps({'message' : 'something is Wrong !!'} , status = 500))
    
    finally :
        session.close()
        return resp


@activity.route('/activity/socialworker/<int:socialworker_id>' , methods=['GET'] )
def getActivityBySocialWorker(socialworker_id):
    
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)
    try : 
        activities = session.query(Activity).filter_by(socialworker_id = socialworker_id)
        r = {}
        for a in activities:
            res = {
                'id' : a.id,
                'activityCode' : a.activityCode, 
            }
            r[a.id] = res

        resp = Response(json.dumps(r) , status=200)
    
    except Exception as e :
        print(e)
        resp = Response(json.dumps({'message' : 'something is Wrong !!'} , status = 500))
    
    finally :
        session.close()
        return resp


@activity.route('/activity/id/<int:activityId>' , methods=['GET'] )
def getActivityById(activityId):
    
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)
    try : 
        activities = session.query(Activity).filter_by(id = activityId)
        r = {}
        for a in activities:
            res = {
                'socialworker_id' : a.socialworker_id,
                'activityCode' : a.activityCode, 
            }
            r[a.id] = res

        resp = Response(json.dumps(r) , status=200)
    
    except Exception as e :
        print(e)
        resp = Response(json.dumps({'message' : 'something is Wrong !!'} , status = 500))
    
    finally :
        session.close()
        return resp
