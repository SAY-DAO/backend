from flask import Flask
from flask import Blueprint , Response , request , json, abort
import requests

search = Blueprint('search' , __name__)

externalHeaders = {"accept": "application/json" , 'Access-Control-Allow-Origin':'*'}
responseHeaders = {'Access-Control-Allow-Origin':'*'}

def getRequest(url):
    return requests.get(url , headers = externalHeaders ).json()

def postRequest(url , data):
    return requests.post(url , headers = externalHeaders , json = data.json())

def randomChild(user_id):
    try : 
        random_child = 'http://94.130.122.6:5200/api/v1/search/SayBrain/'+str(user_id)
        random_child_data = getRequest(random_child)
        return random_child_data['data']
    except Exception as e:
        print(e)
        return None




@search.route('/search/<int:user_id>' , methods= ['GET'])
def searchChildByUserId(user_id):
    try : 
        user_child_url = 'http://94.130.122.6:5200/api/v1/child/user?Id='+str(user_id)
        user_child_data = getRequest(user_child_url)
        rChild = {}
        notNew = True
        while notNew : 
            rChild = randomChild(user_id)       
            notNewChild = False
            for c in user_child_data['data']:
                if c['id'] == rChild['id'] :
                    notNewChild = True
                    break
            notNew = notNewChild

        resp = Response(json.dumps(rChild) , status=200 , mimetype='application/json')
    
    except Exception as e :
        print(e)
        resp = Response(json.dumps({'message' : 'something is wrong !!!'}) , status= 500)

    finally :
        return resp 
