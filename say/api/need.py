from flask import Flask
from flask import Blueprint , Response , request , json, abort
import requests

need = Blueprint('need' , __name__)

externalHeaders = {"accept": "application/json" , 'Access-Control-Allow-Origin':'*'}
responseHeaders = {'Access-Control-Allow-Origin':'*'}




def getRequest(url):
    return requests.get(url , headers = externalHeaders ).json()

def postRequest(url , data):
    return requests.post(url , headers = externalHeaders , json = data.json())

@need.route('/need/<int:need_id>' , methods=['GET'])
def needApi(need_id):

    try:
        need_url = 'http://94.130.122.6:5200/api/v1/need?Id='+str(need_id)

        need_respond = getRequest(need_url)

        need_url_pay = 'http://127.0.0.1:5100/payment/need/'+str(need_id)

        need_respond_pay = getRequest(need_url_pay)

        need_respond['data']['payment'] = need_respond_pay

        resp = Response(json.dumps(need_respond) , status= 200 , mimetype='application/json' , headers=responseHeaders)

    except Exception as e :

        print(e)
        resp = Response(json.dumps({'message' : 'something is wrong !!!'}) , status= 500)

    finally :
        return resp 


