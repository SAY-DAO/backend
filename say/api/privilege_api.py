from say.models import session, obj_to_dict
from say.models.privilege_model import PrivilegeModel
from . import *

"""
Privilege APIs
"""


class GetAllPrivileges(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/privilege/all.yml")
    def get(self):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            privileges = session.query(PrivilegeModel).all()

            result = {}
            for privilege in privileges:
                res =  obj_to_dict(privilege)
                result[str(privilege.id)] = res

            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "Something is Wrong !!!"}), 500)

        finally:
            session.close()
            return resp


class AddPrivilege(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/privilege/add.yml")
    def post(self):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            name = request.form["name"]
            privilege = request.form["privilege"]
            new_privilege = PrivilegeModel(name=name, privilege=privilege)

            session.add(new_privilege)
            session.commit()

            resp = make_response(jsonify({"message": "new Privilege is added"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is wrong"}), 500)

        finally:
            session.close()
            return resp


class GetPrivilegeByName(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/privilege/name.yml")
    def get(self, name):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            privilege_list = session.query(PrivilegeModel).filter_by(name=name).all()

            result = {}
            for privilege in privilege_list:
                res = {"Id": privilege.id, "Privilege": privilege.privilege}
                result[str(privilege.id)] = res

            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is Wrong !!"}), 500)

        finally:
            session.close()
            return resp


class GetPrivilegeById(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/privilege/id.yml")
    def get(self, privilege_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            privilege = session.query(PrivilegeModel).filter_by(id=privilege_id).first()

            if not privilege:
                resp = make_response(jsonify({"message": "something is Wrong !!"}), 500)
                session.close()
                return resp

            result = obj_to_dict(privilege)
            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is Wrong !!"}), 500)

        finally:
            session.close()
            return resp


class GetPrivilegeByPrivilege(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/privilege/privilege.yml")
    def get(self, privilege_type):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            privilege_list = (
                session.query(PrivilegeModel).filter_by(privilege=privilege_type).all()
            )

            result = {}
            for privilege in privilege_list:
                res = obj_to_dict(privilege)
                result[str(privilege.id)] = res

            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is Wrong !!"}), 500)

        finally:
            session.close()
            return resp


class UpdatePrivilege(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/privilege/update.yml")
    def patch(self, privilege_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_privilege = (
                session.query(PrivilegeModel).filter_by(id=privilege_id).first()
            )

            if "name" in request.form.keys():
                base_privilege.name = request.form["name"]

            if "privilege" in request.form.keys():
                base_privilege.privilege = int(request.form["privilege"])

            res = obj_to_dict(base_privilege)
            session.commit()

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "something is Wrong !!"}), 500)

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
