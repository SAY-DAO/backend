from say.models.user_model import UserModel
from hashlib import md5

from . import *
import os

"""
Authentication APIs
"""


class CheckUser(Resource):
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}


        try : 
            if 'username' in request.json.keys():
                username = request.json['username']
            else:
                return Response(json.dumps({'message' : 'userName is needed !!!'}) , status = 500)

            alreadyTaken = session.query(UserModel).filter_by(isDeleted=False).filter_by(userName=username).first()
            if alreadyTaken is not None:
                resp = Response(json.dumps({'status' : False , 'Message' : 'UserName is Already Taken'}) , status = 200)
            else :
                resp = Response(json.dumps({'status' : True , 'Message' : 'UserName is Acceptable'}) , status = 200)
        
        except Exception as e : 
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))
        
        finally : 
            session.close()
            return resp


class RegisterUser(Resource):
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message' : 'fucked'}
        try :
            if 'username' in request.json.keys():
                username = request.json['username']
            else:
                return Response(json.dumps({'message' : 'userName is needed !!!'}) , status = 500)
            
            if 'password' in request.json.keys():
                password = md5(request.json['password'].encode()).hexdigest()
            else : 
                return Response(json.dumps({'message' : 'password is needed !!!'}) , status = 500)
            

            if 'email' in request.json.keys():
                email = request.json['email']
            else : 
                return Response(json.dumps({'message'  : 'email is needed'}) , status = 500)

            alreadyExist = session.query(UserModel).filter_by(isDeleted=False).filter_by(userName=username).first()
            if alreadyExist is not None:
                resp = Response(json.dumps({'status' : False , 'Message' : 'User is Already existed'}) , status = 200)
            else :
                token = md5((username+email).encode()).hexdigest()
                

                created_at = datetime.now()
                last_update = datetime.now()
                last_login = datetime.now()
                
                new_user = UserModel(
                    firstName='',
                    lastName='',
                    userName=username,
                    avatarUrl=None,
                    phoneNumber=None,
                    emailAddress=email,
                    gender=None,
                    city=0,
                    country=0,
                    createdAt=created_at,
                    lastUpdate=last_update,
                    birthDate=None,
                    birthPlace=None,
                    lastLogin=last_login,
                    password=password,
                    flagUrl='',
                    token= token
                )

                session.add(new_user)
                session.commit()

                resp = Response(json.dumps({'message': 'USER Registered SUCCESSFULLY!', 'userToken' : token}) , status = 200)

        except Exception as e :
            print(e)
            resp = Response(json.dumps({'message': 'Something is Wrong!'}) , status = 500)
        
        finally : 
            session.close()
            return resp
                

class Login(Resource):
    def post(self): 
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message' : 'fuck'}


        try: 
            
            if 'username' in request.json.keys() :
                username  = request.json['username']
            else : 
                return Response(json.dumps({'message' : 'userName is needed !!!'}) , status = 500)
            
            if 'password' in request.json.keys():
                password = md5(request.json['password'].encode()).hexdigest()
            else : 
                return Response(json.dumps({'message' : 'password is needed !!!'}) , status = 500)

            

            user = session.query(UserModel).filter_by(isDeleted=False).filter_by(userName=username).first()
            if user is not None : 
                if user.password == password : 
                    user.token = md5((username + user.emailAddress).encode()).hexdigest()
                    user.lastLogin = datetime.now()
                    session.commit()
                    resp = Response(json.dumps({'message' : 'Login Successful' , 'userToken' : user.token}) , status = 200)
                else: 
                    resp = Response(json.dumps({'message' : 'UserName or Password is Wrong'}) , status = 303)


            else : 
                resp = Response(json.dumps({'message' : 'Please Register First'}) , status = 303)
            
        except Exception as e : 
            print(e)
            resp = Response(json.dumps({'message' :'something is wrong'}) , status = 500)
        
        finally : 
            session.close()
            return resp


class Logout(Resource):
    def post(self , user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message' : 'fuck'}

        try :
            user = session.query(UserModel).filter_by(id = user_id).first()
            user.token = ''
            session.commit()
            resp = Response(json.dumps({'message' : 'user is successfully logged out.'}) , status = 200)

        except Exception as e:
            print(e)    
            resp = Response(json.dumps({'message': 'Something is Wrong!'}) , status = 500)

        finally :
            session.close()
            return resp




"""
API URLs
"""



api.add_resource(CheckUser , '/api/v2/auth/checkUserName')
api.add_resource(RegisterUser, '/api/v2/auth/register')
api.add_resource(Login, '/api/v2/auth/login')
api.add_resource(Logout, '/api/v2/auth/logout/userid=<user_id>')