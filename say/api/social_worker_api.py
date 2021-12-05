import os
from datetime import datetime
from hashlib import md5
from uuid import uuid4

from email_validator import EmailNotValidError
from email_validator import validate_email
from flasgger import swag_from
from flask import request
from flask_restful import Resource

from say.models import Child
from say.models import commit
from say.models import obj_to_dict
from say.models.ngo_model import Ngo
from say.models.social_worker_model import SocialWorker
from say.orm import safe_commit
from say.orm import session
from say.validations import validate_password

from ..authorization import authorize
from ..authorization import get_user_id
from ..authorization import get_user_role
from ..decorators import json
from ..decorators import validate
from ..exceptions import HTTP_BAD_REQUEST
from ..exceptions import HTTP_NOT_FOUND
from ..exceptions import HTTP_PERMISION_DENIED
from ..exceptions import HTTPException
from ..roles import *
from ..schema.social_worker import MigrateSocialWorkerChildrenSchema
from ..schema.social_worker import NewSocialWorkerSchema
from ..schema.social_worker import SocialWorkerSchema
from ..validations import valid_image_extension
from .ext import api


'''
Social Worker APIs
'''


class GetAllSocialWorkers(Resource):
    @authorize(
        COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @json
    @swag_from('./docs/social_worker/all.yml')
    def get(self):
        social_workers = session.query(SocialWorker).filter_by(isDeleted=False)

        if get_user_role() in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
            user_id = get_user_id()
            user = session.query(SocialWorker).get(user_id)
            social_workers = social_workers.filter_by(id_ngo=user.id_ngo)

        fetch = {}
        for social_worker in social_workers:
            data = obj_to_dict(social_worker)
            data['typeName'] = social_worker.privilege.name
            data['ngoName'] = social_worker.ngo.name
            fetch[str(social_worker.id)] = data

        return fetch


class AddSocialWorker(Resource):
    @authorize(SUPER_ADMIN)  # TODO: priv
    @validate(NewSocialWorkerSchema)
    @json(SocialWorkerSchema)
    @swag_from('./docs/social_worker/add.yml')
    def post(self, data: NewSocialWorkerSchema):
        ngo = (
            session.query(Ngo)
            .filter(
                Ngo.isDeleted.is_(False),
                Ngo.id == data.id_ngo,
            )
            .populate_existing()
            .with_for_update()
            .one_or_none()
        )

        if ngo is None:
            raise HTTP_BAD_REQUEST(message='NGO not found')

        generated_code = format(data.id_ngo, '03d') + format(
            ngo.socialWorkerCount + 1,
            '03d',
        )

        username = f'sw{generated_code}'
        password = SocialWorker.generate_password()

        new_social_worker = SocialWorker(
            userName=username,
            password=password,
            generatedCode=generated_code,
            **data.dict(),
        )

        session.add(new_social_worker)
        safe_commit(session)
        new_social_worker.send_password(password=password)
        return new_social_worker


class GetSocialWorkerById(Resource):
    @authorize(
        COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @json
    @swag_from('./docs/social_worker/id.yml')
    def get(self, social_worker_id):
        social_worker_query = (
            session.query(SocialWorker)
            .filter_by(id=social_worker_id)
            .filter_by(isDeleted=False)
        )

        if get_user_role() in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
            user_id = get_user_id()
            user = session.query(SocialWorker).get(user_id)
            social_worker_query = social_worker_query.filter_by(id_ngo=user.id_ngo)

        social_worker = social_worker_query.first()

        if not social_worker:
            raise HTTP_NOT_FOUND()

        res = obj_to_dict(social_worker)
        res['typeName'] = social_worker.privilege.name
        res['ngoName'] = social_worker.ngo.name if social_worker.id_ngo != 0 else 'SAY'
        return res


class GetSocialWorkerByNgoId(Resource):
    @authorize(
        COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @json
    @swag_from('./docs/social_worker/ngo.yml')
    def get(self, ngo_id):
        ngo_id = int(ngo_id)
        social_workers = (
            session.query(SocialWorker)
            .filter_by(id_ngo=ngo_id)
            .filter_by(isDeleted=False)
        )

        if get_user_role() in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
            user_id = get_user_id()
            user = session.query(SocialWorker).get(user_id)
            if user.id_ngo != ngo_id:
                raise HTTP_PERMISION_DENIED()

        fetch = {}
        for social_worker in social_workers:
            if not social_worker:
                raise HTTP_NOT_FOUND()

            data = obj_to_dict(social_worker)
            data['typeName'] = social_worker.privilege.name
            data['ngoName'] = (
                social_worker.ngo.name if social_worker.id_ngo != 0 else 'SAY'
            )

            fetch[str(social_worker.id)] = data

        return fetch


class UpdateSocialWorker(Resource):
    @authorize(
        COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @json
    @swag_from('./docs/social_worker/update.yml')
    def patch(self, social_worker_id):
        ngo_change = False
        previous_ngo = None
        base_social_worker = (
            session.query(SocialWorker)
            .filter_by(id=social_worker_id)
            .filter_by(isDeleted=False)
            .one_or_none()
        )
        if base_social_worker is None:
            raise HTTP_NOT_FOUND()

        if get_user_role() in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
            user_id = get_user_id()
            user = session.query(SocialWorker).one_or_none(user_id)
            if user is None or user.id_ngo != base_social_worker.id_ngo:
                raise HTTP_PERMISION_DENIED()

        if 'idCardUrl' in request.files.keys():
            id_card_file = request.files['idCardUrl']
            if valid_image_extension(id_card_file):
                base_social_worker.idCardUrl = id_card_file
            else:
                return {'message': 'invalid id card file!'}, 400

        if 'passportUrl' in request.files.keys():
            passport_file = request.files['passportUrl']
            if valid_image_extension(passport_file):
                base_social_worker.passportUrl = passport_file
            else:
                return {'message': 'invalid passport file!'}, 400

        if 'avatarUrl' in request.files.keys():
            avatar_file = request.files['avatarUrl']
            if valid_image_extension(avatar_file):
                base_social_worker.avatarUrl = avatar_file
            else:
                return {'message': 'invalid avatar file!'}, 400

        if 'id_ngo' in request.form.keys():
            previous_ngo = base_social_worker.id_ngo
            base_social_worker.id_ngo = int(request.form['id_ngo'])
            ngo_change = True

        if 'country' in request.form.keys():
            base_social_worker.country = int(request.form['country'])

        if 'city' in request.form.keys():
            base_social_worker.city = int(request.form['city'])

        if 'id_type' in request.form.keys():
            base_social_worker.id_type = int(request.form['id_type'])

        if 'firstName' in request.form.keys():
            base_social_worker.firstName = request.form['firstName']

        if 'lastName' in request.form.keys():
            base_social_worker.lastName = request.form['lastName']

        if 'userName' in request.form.keys():
            base_social_worker.userName = request.form['userName']

        if 'birthCertificateNumber' in request.form.keys():
            base_social_worker.birthCertificateNumber = request.form[
                'birthCertificateNumber'
            ]

        if 'idNumber' in request.form.keys():
            base_social_worker.idNumber = request.form['idNumber']

        if 'passportNumber' in request.form.keys():
            base_social_worker.passportNumber = request.form['passportNumber']

        if 'gender' in request.form.keys():
            base_social_worker.gender = (
                True if request.form['gender'] == 'true' else False
            )

        if 'birthDate' in request.form.keys():
            base_social_worker.birthDate = datetime.strptime(
                request.form['birthDate'], '%Y-%m-%d'
            )

        if 'phoneNumber' in request.form.keys():
            base_social_worker.phoneNumber = request.form['phoneNumber']

        if 'emergencyPhoneNumber' in request.form.keys():
            base_social_worker.emergencyPhoneNumber = request.form['emergencyPhoneNumber']

        if 'emailAddress' in request.form.keys():
            base_social_worker.emailAddress = request.form['emailAddress']

        if 'telegramId' in request.form.keys():
            base_social_worker.telegramId = request.form['telegramId']

        if 'postalAddress' in request.form.keys():
            base_social_worker.postalAddress = request.form['postalAddress']

        if 'bankAccountNumber' in request.form.keys():
            base_social_worker.bankAccountNumber = request.form['bankAccountNumber']

        if 'bankAccountShebaNumber' in request.form.keys():
            base_social_worker.bankAccountShebaNumber = request.form[
                'bankAccountShebaNumber'
            ]

        if 'bankAccountCardNumber' in request.form.keys():
            base_social_worker.bankAccountCardNumber = request.form[
                'bankAccountCardNumber'
            ]

        if 'password' in request.form.keys():
            password = request.form['password']
            if not validate_password(password):
                raise HTTPException(
                    status_code=400,
                    message='password must be atleast 6 character',
                )
            base_social_worker.password = password

        if ngo_change:
            that_ngo = (
                session.query(Ngo)
                .filter_by(id=previous_ngo)
                .filter_by(isDeleted=False)
                .first()
            )
            this_ngo = (
                session.query(Ngo)
                .filter_by(id=base_social_worker.id_ngo)
                .filter_by(isDeleted=False)
                .first()
            )

            that_ngo.currentChildrenCount -= base_social_worker.currentChildCount
            that_ngo.currentSocialWorkerCount -= 1

            this_ngo.currentChildrenCount += base_social_worker.currentChildCount
            this_ngo.currentSocialWorkerCount += 1

            this_ngo.childrenCount += base_social_worker.childCount
            this_ngo.socialWorkerCount += 1

        session.add(base_social_worker)
        safe_commit(session)
        return base_social_worker


class DeleteSocialWorker(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/social_worker/delete.yml')
    def patch(self, social_worker_id):
        base_social_worker = (
            session.query(SocialWorker)
            .filter_by(id=social_worker_id)
            .filter_by(isDeleted=False)
            .first()
        )

        base_social_worker.isDeleted = True
        this_ngo = (
            session.query(Ngo)
            .filter_by(id=base_social_worker.id_ngo)
            .filter_by(isDeleted=False)
            .one_or_none()
        )

        this_ngo.currentChildrenCount -= base_social_worker.currentChildCount
        this_ngo.currentSocialWorkerCount -= 1

        safe_commit(session)
        return {'message': 'social worker deleted successfully!'}


class DeactivateSocialWorker(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @commit
    @swag_from('./docs/social_worker/deactivate.yml')
    def patch(self, social_worker_id):

        sw = (
            session.query(SocialWorker)
            .filter_by(id=social_worker_id)
            .filter_by(isDeleted=False)
            .filter_by(isActive=True)
            .with_for_update()
            .one_or_none()
        )

        if not sw:
            return {
                'message': f'Social worker {social_worker_id} not found',
            }, 404

        has_active_child = (
            session.query(Child.id)
            .filter(Child.id_social_worker == social_worker_id)
            .filter(Child.isConfirmed.is_(True))
            .filter(Child.isDeleted.is_(False))
            .filter(Child.isMigrated.is_(False))
            .count()
        )

        if has_active_child:
            return {
                'message': f'Social worker {social_worker_id} has active'
                f' children and can not deactivate',
            }, 400

        sw.isActive = False
        return sw


class ActivateSocialWorker(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/social_worker/activate.yml')
    def patch(self, social_worker_id):
        base_social_worker = (
            session.query(SocialWorker)
            .filter_by(id=social_worker_id)
            .filter_by(isDeleted=False)
            .first()
        )

        base_social_worker.isActive = True

        safe_commit(session)
        return base_social_worker


class MigrateSocialWorkerChildren(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @commit
    @swag_from('./docs/social_worker/migrate_children.yml')
    def post(self, id):
        try:
            data = MigrateSocialWorkerChildrenSchema(
                **request.form.to_dict(),
            )
        except ValueError as ex:
            return ex.json(), 400

        if data.destination_social_worker_id == id:
            return {'message': 'Can not migrate to same sw'}, 400

        sw = (
            session.query(SocialWorker)
            .filter_by(id=id)
            .filter_by(isDeleted=False)
            .filter_by(isActive=True)
            .with_for_update(SocialWorker)
            .one_or_none()
        )

        if not sw:
            return {
                'message': f'Social worker {id} not found',
            }, 404

        destination_sw = (
            session.query(SocialWorker)
            .filter_by(id=data.destination_social_worker_id)
            .filter_by(isDeleted=False)
            .filter_by(isActive=True)
            .with_for_update()
            .one_or_none()
        )

        if not destination_sw:
            return {
                'message': f'destination social worker not found',
            }, 400

        children = (
            session.query(Child)
            .filter(Child.id_social_worker == id)
            .filter(Child.isDeleted.is_(False))
            .with_for_update()
        )

        resp = []
        for child in children:
            migration = child.migrate(destination_sw)
            resp.append(migration)
        return resp


api.add_resource(GetAllSocialWorkers, '/api/v2/socialWorker/all')
api.add_resource(AddSocialWorker, '/api/v2/socialWorker/add')
api.add_resource(
    GetSocialWorkerById,
    '/api/v2/socialWorker/socialWorkerId=<social_worker_id>',
)
api.add_resource(GetSocialWorkerByNgoId, '/api/v2/socialWorker/ngoId=<ngo_id>')
api.add_resource(
    UpdateSocialWorker,
    '/api/v2/socialWorker/update/socialWorkerId=<social_worker_id>',
)
api.add_resource(
    DeleteSocialWorker,
    '/api/v2/socialWorker/delete/socialWorkerId=<social_worker_id>',
)
api.add_resource(
    DeactivateSocialWorker,
    '/api/v2/socialWorker/deactivate/socialWorkerId=<social_worker_id>',
)
api.add_resource(
    ActivateSocialWorker,
    '/api/v2/socialWorker/activate/socialWorkerId=<social_worker_id>',
)

api.add_resource(
    MigrateSocialWorkerChildren,
    '/api/v2/socialWorker/<int:id>/children/migrate',
)
