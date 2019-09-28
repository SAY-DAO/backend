from say.models.privilege_model import PrivilegeModel
from . import *

"""
Privilege APIs
"""


class GetAllPrivileges(Resource):
    @swag_from("./docs/privilege/all.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            privileges = session.query(PrivilegeModel).all()

            result = {}
            for privilege in privileges:
                res = {
                    "Id": privilege.id,
                    "Name": privilege.name,
                    "Privilege": privilege.privilege,
                }
                result[str(privilege.id)] = res

            resp = Response(utf8_response(result, True), status=200)

        except Exception as e:
            print(e)
            resp = Response(
                json.dumps({"message": "Something is Wrong !!!"}), status=500
            )

        finally:
            session.close()
            return resp


class AddPrivilege(Resource):
    @swag_from("./docs/privilege/add.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            name = request.form["name"]
            privilege = request.form["privilege"]
            new_privilege = PrivilegeModel(name=name, privilege=privilege)

            session.add(new_privilege)
            session.commit()

            resp = Response(
                json.dumps({"message": "new Privilege is added"}), status=200
            )

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "something is wrong"}), status=200)

        finally:
            session.close()
            return resp


class GetPrivilegeByName(Resource):
    @swag_from("./docs/privilege/name.yml")
    def get(self, name):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            privilege_list = session.query(PrivilegeModel).filter_by(name=name).all()

            result = {}
            for privilege in privilege_list:
                res = {"Id": privilege.id, "Privilege": privilege.privilege}
                result[str(privilege.id)] = res

            resp = Response(utf8_response(result, True), status=200)

        except Exception as e:
            print(e)
            resp = Response(
                json.dumps({"message": "something is Wrong !!"}, status=500)
            )

        finally:
            session.close()
            return resp


class GetPrivilegeById(Resource):
    @swag_from("./docs/privilege/id.yml")
    def get(self, privilege_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            privilege = session.query(PrivilegeModel).filter_by(id=privilege_id).first()

            if not privilege:
                resp = Response(
                    json.dumps({"message": "something is Wrong !!"}, status=500)
                )
                session.close()
                return resp

            result = obj_to_dict(privilege)
            resp = Response(utf8_response(result), status=200)

        except Exception as e:
            print(e)
            resp = Response(
                json.dumps({"message": "something is Wrong !!"}, status=500)
            )

        finally:
            session.close()
            return resp


class GetPrivilegeByPrivilege(Resource):
    @swag_from("./docs/privilege/privilege.yml")
    def get(self, privilege_type):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            privilege_list = (
                session.query(PrivilegeModel).filter_by(privilege=privilege_type).all()
            )

            result = {}
            for privilege in privilege_list:
                res = {"Id": privilege.id, "Name": privilege.name}
                result[str(privilege.id)] = res

            resp = Response(utf8_response(result, True), status=200)

        except Exception as e:
            print(e)
            resp = Response(
                json.dumps({"message": "something is Wrong !!"}, status=500)
            )

        finally:
            session.close()
            return resp


class UpdatePrivilege(Resource):
    @swag_from("./docs/privilege/update.yml")
    def patch(self, privilege_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            base_privilege = (
                session.query(PrivilegeModel).filter_by(id=privilege_id).first()
            )

            if "name" in request.form.keys():
                base_privilege.name = request.form["name"]

            if "privilege" in request.form.keys():
                base_privilege.privilege = int(request.form["privilege"])

            res = {
                "Id": int(privilege_id),
                "Name": base_privilege.name,
                "Privilege": base_privilege.privilege,
            }

            session.commit()

            resp = Response(utf8_response(res), status=200)

        except Exception as e:
            print(e)
            resp = Response(
                json.dumps({"message": "something is Wrong !!"}, status=500)
            )

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetAllPrivileges, "/api/v2/privilege/all")
api.add_resource(AddPrivilege, "/api/v2/privilege/add")
api.add_resource(GetPrivilegeByName, "/api/v2/privilege/name=<name>")
api.add_resource(GetPrivilegeById, "/api/v2/privilege/privilegeId=<privilege_id>")
api.add_resource(
    GetPrivilegeByPrivilege, "/api/v2/privilege/privilege=<privilege_type>"
)
api.add_resource(UpdatePrivilege, "/api/v2/privilege/update/privilegeId=<privilege_id>")
