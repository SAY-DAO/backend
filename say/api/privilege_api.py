from say.models.privilege_model import PrivilegeModel
from . import *

"""
Privilege APIs
"""


class GetAllPrivileges(Resource):
    @swag_from('./apidocs/privilege/all.yml')
    def get(self):
        Session = sessionmaker(db)
        session = Session()


        try:
            privileges = session.query(PrivilegeModel).all()
            r = {}
            for p in privileges:
                res = {
                    'Id': p.Id,
                    'Name': p.Name,
                    'Privilege': p.Privilege
                }
                r[p.Id] = res

            resp = Response(json.dumps(r), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'Something is Wrong !!!'}), status=500)
        finally:
            session.close()
            return resp


class AddPrivilege(Resource):
    @swag_from('./apidocs/privilege/add.yml')
    def post(self):
        Session = sessionmaker(db)
        session = Session()

        try:
            name = request.json['Name']
            privilege = request.json['Privilege']
            new_privilege = PrivilegeModel(Name=name, Privilege=privilege)
            session.add(new_privilege)
            session.commit()

            resp = Response(json.dumps({'message': 'new Privilege is added'}), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'something is wrong'}), status=200)

        finally:
            session.close()
            return resp


class GetPrivilegeByName(Resource):
    @swag_from('./apidocs/privilege/name.yml')
    def get(self, name):
        Session = sessionmaker(db)
        session = Session()

        try:
            privelegesList = session.query(PrivilegeModel).filter_by(Name=name).all()
            r = {}
            for p in privelegesList:
                res = {
                    'Id': p.Id,
                    'Privilege': p.Privilege
                }
                r[p.Id] = res

            resp = Response(json.dumps(r), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'something is Wrong !!'}, status=500))

        finally:
            session.close()
            return resp


class GetPrivilegeById(Resource):
    @swag_from('./apidocs/privilege/id.yml')
    def get(self, privilege_id):
        Session = sessionmaker(db)
        session = Session()

        try:
            privelegesList = session.query(PrivilegeModel).filter_by(Id=privilege_id).first()

            if not privelegesList:
                resp = Response(json.dumps({'message': 'something is Wrong !!'}, status=500))
                session.close()
                return resp

            resp = Response(json.dumps(obj_to_dict(privelegesList)), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'something is Wrong !!'}, status=500))

        finally:
            session.close()
            return resp


class GetPrivilegeByPrivilege(Resource):
    @swag_from('./apidocs/privilege/privilege.yml')
    def get(self, privilege_type):
        Session = sessionmaker(db)
        session = Session()

        try:
            privelegesList = session.query(PrivilegeModel).filter_by(Privilege=privilege_type).all()
            r = {}
            for p in privelegesList:
                res = {
                    'Id': p.Id,
                    'Name': p.Name
                }
                r[p.Id] = res

            resp = Response(json.dumps(r), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'something is Wrong !!'}, status=500))

        finally:
            session.close()
            return resp


class UpdatePrivilege(Resource):
    @swag_from('./apidocs/privilege/update.yml')
    def patch(self, privilege_id):
        Session = sessionmaker(db)
        session = Session()

        try:
            base_privilege = session.query(PrivilegeModel).filter_by(Id=privilege_id).first()
            print(base_privilege)
            if 'Name' in request.json.keys():
                base_privilege.Name = request.json['Name']
            if 'Privilege' in request.json.keys():
                base_privilege.Privilege = request.json['Privilege']
            res = {
                'Id': privilege_id,
                'Name': base_privilege.Name,
                'Privilege': base_privilege.Privilege
            }
            session.commit()

            resp = Response(json.dumps({'message': 'privilege updated successfully!'}), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'something is Wrong !!'}, status=500))
        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetAllPrivileges, '/api/v2/privilege/all')
api.add_resource(AddPrivilege, '/api/v2/privilege/add')
api.add_resource(GetPrivilegeByName, '/api/v2/privilege/name=<name>')
api.add_resource(GetPrivilegeById, '/api/v2/privilege/privilegeId=<privilege_id>')
api.add_resource(GetPrivilegeByPrivilege, '/api/v2/privilege/privilege=<privilege_type>')
api.add_resource(UpdatePrivilege, '/api/v2/privilege/update/privilegeId=<privilege_id>')
