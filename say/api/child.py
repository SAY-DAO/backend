from flask import Flask
from flask import Blueprint , Response , request , json, abort
import requests

child = Blueprint('child' , __name__)

externalHeaders = {"accept": "application/json" , 'Access-Control-Allow-Origin':'*'}
responseHeaders = {'Access-Control-Allow-Origin':'*'}



@child.route('child/<int:child_id>' , methods=['GET'])
def childApi(child_id):
    try : 
    
        child_url = 'http://94.130.122.6:5200/api/v1/child?Id='+str(child_id)

        child_respond = getRequest(child_url)


        family_url = 'http://94.130.122.6:5200/api/v1/family/'+str(child_id)
        family_respond = getRequest(family_url)

        child_respond['data']['family'] = family_respond['data']

        resp = Response(json.dumps(child_respond) , status= 200 , mimetype='application/json' , headers=responseHeaders)

    except Exception as e :
        print(e)
        resp = Response(json.dumps({'message' : 'something is wrong !!!'}) , status= 500)
    
    finally: 
        return resp


@child.route('child/user/<int:user_id>' , methods=['GET'])
def getChildByUserId(user_id):
    try :
        child_url = 'http://94.130.122.6:5200/api/v1/child/user?Id='+str(user_id)

        child_respond = getRequest(child_url)

        resp = Response(json.dumps(child_respond) , status=200 , mimetype='application/json' , headers=responseHeaders)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'something is wrong !!!'}) , status= 500)

    finally:
        return resp



def getRequest(url):
    return requests.get(url , headers = externalHeaders ).json()