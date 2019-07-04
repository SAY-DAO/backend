from flask import Flask
from flask import Blueprint , Response , request , json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from say.config import db

from say.models import Privileges


privilege = Blueprint('privilege' , __name__)

base = declarative_base()

@privilege.route('/privilege' , methods = ['GET' , 'POST'])
def api_privilege():
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)

    if request.method == 'GET':
        try : 
            privileges = session.query(Privileges)
            r = {}
            for p in privileges:
                res = {
                    'id' : p.id,
                    'name' : p.name,
                    'privilege' : p.privilege
                }
                r[p.id] = res
            
            resp = Response(json.dumps(r) , status=200)
        
        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message' : 'Something is Wrong !!!'}) , status=500)
        finally :
            session.close()
            return resp

    if request.method == 'POST':

        name = request.form['name']
        privilege = request.form['privilege']

        try : 
            new_privilege = Privileges(name = name , privilege = privilege)
            session.add(new_privilege)
            session.commit()

            resp = Response(json.dumps({'message' : 'new Privilege is added'}) , status=200)
        
        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message' : 'something is wrong'}) , status=200)
        
        finally : 
            session.close()
            return resp
            
@privilege.route('/privilege/name/<name>' , methods = ['GET'])
def getPrivilegeByName(name):
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)


    try: 
        privelegesList = session.query(Privileges).filter_by(name = name)
        r = {}
        for p in privelegesList:
            res = {
                'id' : p.id,
                'privelege' : p.privilege
            }
            r[p.id] = res
        
        resp = Response(json.dumps(r) , status= 200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'something is Wrong !!'} , status = 500))

    finally :
        session.close()
        return resp


@privilege.route('/privilege/id/<int:privilege_id>' , methods = ['GET'])
def getPrivilegeById(privilege_id):
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)


    try: 
        privelegesList = session.query(Privileges).filter_by(id = privilege_id)
        r = {}
        for p in privelegesList:
            res = {
                'name' : p.name,
                'privilege' : p.privilege
            }
            r[p.id] = res
        
        resp = Response(json.dumps(r) , status= 200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'something is Wrong !!'} , status = 500))

    finally :
        session.close()
        # resp = json.dumps({})
        return resp

@privilege.route('/privilege/privilege/<int:privilege_type>' , methods = ['GET'])
def getPrivilegeByPrivelege(privilege_type):
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)


    try: 
        privelegesList = session.query(Privileges).filter_by(privilege	 = privilege_type)
        r = {}
        for p in privelegesList:
            res = {
                'id' : p.id,
                'name' : p.name
            }
            r[p.id] = res
        
        resp = Response(json.dumps(r) , status= 200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'something is Wrong !!'} , status = 500))

    finally :
        session.close()
        return resp

@privilege.route('/privilege/update/<int:privilege_id>' , methods = ['patch'])
def updatePrivilege(privilege_id):
    Session = sessionmaker(db)
    session = Session()
    base.metadata.create_all(db)

    try : 
        base_privilege = session.query(Privileges).filter_by(id = privilege_id).first()
        print(base_privilege)
        if 'name' in request.form.keys() :
            base_privilege.name = request.form['name']
        if 'privilege' in request.form.keys() :
            base_privilege.privilege = request.form['privilege']
        res = {
            'id' : privilege_id,
            'name' : base_privilege.name,
            'privilege' : base_privilege.privilege
        }
        session.commit()
        
        resp = Response(json.dumps(res) , status=200)
    
    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'something is Wrong !!'} , status = 500))
    finally :
        session.close()
        return resp