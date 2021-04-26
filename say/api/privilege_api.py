from flasgger import swag_from
from flask import request
from flask_restful import Resource

from say.api.ext import api
from say.authorization import authorize
from say.decorators import json
from say.exceptions import HTTP_NOT_FOUND
from say.models import obj_to_dict
from say.models.privilege_model import Privilege
from say.orm import safe_commit
from say.orm import session
from say.roles import *


'''
Privilege APIs
'''


class GetAllPrivileges(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/privilege/all.yml')
    def get(self):
        privileges = session.query(Privilege).all()

        result = {}
        for privilege in privileges:
            res = obj_to_dict(privilege)
            result[str(privilege.id)] = res

        return result


class AddPrivilege(Resource):

    @authorize(SUPER_ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/privilege/add.yml')
    def post(self):
        name = request.form['name']
        privilege = request.form['privilege']
        new_privilege = Privilege(name=name, privilege=privilege)

        session.add(new_privilege)
        safe_commit(session)

        return new_privilege


class GetPrivilegeByName(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/privilege/name.yml')
    def get(self, name):
        privilege_list = session.query(Privilege).filter_by(name=name).all()

        result = {}
        for privilege in privilege_list:
            res = {'Id': privilege.id, 'Privilege': privilege.privilege}
            result[str(privilege.id)] = res

        return result


class GetPrivilegeById(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/privilege/id.yml')
    def get(self, privilege_id):
        privilege = session.query(Privilege) \
            .filter_by(id=privilege_id) \
            .one_or_none()

        if not privilege:
            raise HTTP_NOT_FOUND()

        return privilege


class GetPrivilegeByPrivilege(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/privilege/privilege.yml')
    def get(self, privilege_type):

        privilege_list = session.query(Privilege) \
            .filter_by(privilege=privilege_type) \
            .all()

        result = {}
        for privilege in privilege_list:
            res = obj_to_dict(privilege)
            result[str(privilege.id)] = res

        return result


class UpdatePrivilege(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/privilege/update.yml')
    def patch(self, privilege_id):
        privilege = session.query(Privilege) \
            .filter_by(id=privilege_id)\
            .one_or_none()

        if not privilege:
            raise HTTP_NOT_FOUND()

        if 'name' in request.form.keys():
            privilege.name = request.form['name']

        if 'privilege' in request.form.keys():
            privilege.privilege = int(request.form['privilege'])

        safe_commit(session)
        return privilege


api.add_resource(GetAllPrivileges, '/api/v2/privilege/all')
api.add_resource(AddPrivilege, '/api/v2/privilege/add')
api.add_resource(GetPrivilegeByName, '/api/v2/privilege/name=<name>')
api.add_resource(GetPrivilegeById, '/api/v2/privilege/privilegeId=<privilege_id>')
api.add_resource(
    GetPrivilegeByPrivilege, '/api/v2/privilege/privilege=<privilege_type>'
)
api.add_resource(UpdatePrivilege, '/api/v2/privilege/update/privilegeId=<privilege_id>')
