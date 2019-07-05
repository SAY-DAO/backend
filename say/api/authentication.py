from flask import Flask
from flask import Blueprint , Response , request , json, abort
import requests

authentication = Blueprint('authentication' , __name__)

externalHeaders = {"accept": "application/json" , 'Access-Control-Allow-Origin':'*'}


@authentication.route('/otp' , methods=['POST'])
def sendOtp():
    
    try :
        phoneNumber = request.form['phoneNumber']
        countryCode = '0098'


        otp_url = 'http://94.130.122.6:5200/api/v1/Auth/SendOtp'
        otp_data = {
            "phoneNumber" : phoneNumber,
            "countryCode" : countryCode
        }
        
        otp_respond = requests.post(otp_url , headers = externalHeaders , json = otp_data)
        otp_respond = otp_respond.json()

        resp = Response(json.dumps(otp_respond) , status=200 , mimetype='application/json' , headers={'Access-Control-Allow-Origin':'*'})
    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'something is wrong !!!'}) , status=500)
    finally:
        return resp


@authentication.route('/register' , methods=['POST'])
def register():

    try:
        phoneNumber = request.form['phoneNumber']
        countryCode = '0098'
        otpCode = request.form['otp']

        register_url = 'http://94.130.122.6:5200/api/v1/Auth/login'  
        register_data = {
            "phoneNumber"  : phoneNumber,
            "countryCode"  : countryCode,
            "otpCode"      : otpCode
        }

        register_respond = requests.post(register_url , headers = externalHeaders , json = register_data)
        register_respond = register_respond.json()

        resp = Response(json.dumps(register_respond) , status=200 , mimetype='application/json' , headers={'Access-Control-Allow-Origin':'*'})
    
    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'something is wrong !!!'}) , status=500)
    
    finally:
        return resp