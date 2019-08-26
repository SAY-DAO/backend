from hashlib import md5

from say.models.user_model import UserModel

from . import *

class registerNewUser(resources):
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}


        try : 

            if 'username' in request.json.keys():
                userName = request.json['username']
            else:
                return respond({'message': 'UserName is not valid'} , status = 500)
            
            if 'password' in request.json.keys():    
                password = request.json['password']
            else:
                return respond(json.dumps({'message': 'password is not valid'}) , status = 500)

            if 'email' in request.json.keys():
                email = request.json['email']
            else :
                return respond(json.dumps({'message': 'email is not valid'}) , status = 500)

            sameUser = session.query(UserModel).filter_by(UserName = userName).first()
            if sameUser == {}:
                


