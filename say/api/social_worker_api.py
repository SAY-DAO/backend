import os
from datetime import datetime
from hashlib import md5
from uuid import uuid4

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

from ..authorization import authorize
from ..authorization import get_user_id
from ..authorization import get_user_role
from ..config import configs
from ..decorators import json
from ..exceptions import HTTP_NOT_FOUND
from ..exceptions import HTTP_PERMISION_DENIED
from ..roles import *
from ..schema.social_worker import MigrateSocialWorkerChildrenSchema
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
    panel_users = 0

    @authorize(SUPER_ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/social_worker/add.yml')
    def post(self):
        if 'country' in request.form.keys():
            country = int(request.form['country'])
        else:
            country = None

        if 'city' in request.form.keys():
            city = int(request.form['city'])
        else:
            city = None

        if 'firstName' in request.form.keys():
            first_name = request.form['firstName']
        else:
            first_name = None

        if 'birthCertificateNumber' in request.form.keys():
            birth_certificate_number = request.form['birthCertificateNumber']
        else:
            birth_certificate_number = None

        if 'passportNumber' in request.form.keys():
            passport_number = request.form['passportNumber']
        else:
            passport_number = None

        if 'postalAddress' in request.form.keys():
            postal_address = request.form['postalAddress']
        else:
            postal_address = None

        if 'bankAccountNumber' in request.form.keys():
            bank_account_number = request.form['bankAccountNumber']
        else:
            bank_account_number = None

        if 'bankAccountShebaNumber' in request.form.keys():
            bank_account_sheba_number = request.form['bankAccountShebaNumber']
        else:
            bank_account_sheba_number = None

        if 'bankAccountCardNumber' in request.form.keys():
            bank_account_card_number = request.form['bankAccountCardNumber']
        else:
            bank_account_card_number = None

        if 'birthDate' in request.form.keys():
            birth_date = datetime.strptime(request.form['birthDate'], '%Y-%m-%d')
        else:
            birth_date = None

        telegram_id = request.form['telegramId']
        id_number = request.form['idNumber']
        id_ngo = int(request.form['id_ngo'])
        id_type = int(request.form['id_type'])
        last_name = request.form['lastName']
        gender = True if request.form['gender'] == 'true' else False
        phone_number = request.form['phoneNumber']
        emergency_phone_number = request.form['emergencyPhoneNumber']
        email_address = request.form['emailAddress']
        password = request.form['password']

        register_date = datetime.utcnow()
        last_login_date = datetime.utcnow()

        if id_ngo != 0:
            ngo = (
                session.query(Ngo).filter_by(isDeleted=False).filter_by(id=id_ngo).first()
            )
            generated_code = format(id_ngo, '03d') + format(
                ngo.socialWorkerCount + 1, '03d'
            )

            ngo.socialWorkerCount += 1
            ngo.currentSocialWorkerCount += 1

        else:
            self.panel_users += 1
            generated_code = format(id_ngo, '03d') + format(self.panel_users, '03d')

        username = f'sw{generated_code}'

        new_social_worker = SocialWorker(
            id_ngo=id_ngo,
            country=country,
            city=city,
            id_type=id_type,
            firstName=first_name,
            lastName=last_name,
            userName=username,
            password=password,
            birthCertificateNumber=birth_certificate_number,
            idNumber=id_number,
            gender=gender,
            birthDate=birth_date,
            phoneNumber=phone_number,
            emergencyPhoneNumber=emergency_phone_number,
            emailAddress=email_address,
            telegramId=telegram_id,
            postalAddress=postal_address,
            bankAccountNumber=bank_account_number,
            bankAccountShebaNumber=bank_account_sheba_number,
            bankAccountCardNumber=bank_account_card_number,
            registerDate=register_date,
            lastLoginDate=last_login_date,
            passportNumber=passport_number,
            generatedCode=generated_code,
            passportUrl='',
            avatarUrl='',
            idCardUrl='',
        )

        session.add(new_social_worker)
        session.flush()

        if 'avatarUrl' not in request.files:
            return {'message': 'Avatar is needed'}, 400

        avatar_file = request.files['avatarUrl']
        if extension := valid_image_extension(avatar_file):
            avatar_name = uuid4().hex + extension
            avatar_path = os.path.join(
                configs.UPLOAD_FOLDER,
                'social-workers/avatars',
            )

            if not os.path.isdir(avatar_path):
                os.makedirs(avatar_path, exist_ok=True)

            avatar = os.path.join((avatar_path, avatar_name))
            avatar_file.save(avatar)
            new_social_worker.avatarUrl = avatar
        else:
            return {'message': 'invalid avatar file!'}, 400

        if 'idCardUrl' in request.files:
            id_card_file = request.files['idCardUrl']

            if extension := valid_image_extension(id_card_file):
                id_card_name = uuid4().hex + extension

                id_card_path = os.path.join(
                    configs.UPLOAD_FOLDER, 'social-workers/id-cards'
                )

                if not os.path.isdir(id_card_path):
                    os.makedirs(id_card_path, exist_ok=True)

                id_card = os.path.join(id_card_path, id_card_name)
                id_card_file.save(id_card)
                new_social_worker.idCardUrl = id_card
            else:
                return {'message': 'invalid id card file!'}, 400

        if 'passportUrl' in request.files:
            passport_file = request.files['passportUrl']

            if extension := valid_image_extension(passport_file):
                passport_name = uuid4().hex + extension

                passport_path = os.path.join(
                    configs.UPLOAD_FOLDER, 'social-workers/passports'
                )

                if not os.path.isdir(passport_path):
                    os.makedirs(passport_path, exist_ok=True)

                passport = os.path.join(passport_path, passport_name)
                passport_file.save(passport)
                new_social_worker.passportUrl = passport
            else:
                return {'message': 'invalid passport file!'}, 400

        safe_commit(session)
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
            .first()
        )

        if get_user_role() in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
            user_id = get_user_id()
            user = session.query(SocialWorker).get(user_id)
            if user.id_ngo != base_social_worker.id_ngo:
                raise HTTP_PERMISION_DENIED()

        if 'idCardUrl' in request.files.keys():
            file1 = request.files['idCardUrl']

            if file1.filename == '':
                return {'message': 'ERROR OCCURRED --> EMPTY VOICE!'}, 400

            if extension := valid_image_extension(file1):
                filename1 = base_social_worker.generatedCode + extension

                temp_idcard_path = os.path.join(
                    configs.UPLOAD_FOLDER,
                    str(base_social_worker.id) + '-socialworker',
                )

                if not os.path.isdir(temp_idcard_path):
                    os.makedirs(temp_idcard_path, exist_ok=True)

                for obj in os.listdir(temp_idcard_path):
                    check = str(base_social_worker.id) + '-idcard'
                    if obj.split('_')[0] == check:
                        os.remove(os.path.join(temp_idcard_path, obj))

                base_social_worker.idCardUrl = os.path.join(
                    temp_idcard_path,
                    str(base_social_worker.id) + '-idcard_' + uuid4().hex + filename1,
                )

                file1.save(base_social_worker.idCardUrl)
                base_social_worker.idCardUrl = '/' + base_social_worker.idCardUrl
            else:
                return {'message': 'invalid idcard file!'}, 400

        if 'passportUrl' in request.files.keys():
            file2 = request.files['passportUrl']

            if file2.filename == '':
                return {'message': 'ERROR OCCURRED --> EMPTY Passport!'}, 400

            if extension := valid_image_extension(file2):
                filename2 = base_social_worker.generatedCode + uuid4().hex + extension

                temp_passport_path = os.path.join(
                    configs.UPLOAD_FOLDER,
                    str(base_social_worker.id) + '-socialworker',
                )

                if not os.path.isdir(temp_passport_path):
                    os.makedirs(temp_passport_path, exist_ok=True)

                for obj in os.listdir(temp_passport_path):
                    check = str(base_social_worker.id) + '-passport'
                    if obj.split('_')[0] == check:
                        os.remove(os.path.join(temp_passport_path, obj))

                base_social_worker.passportUrl = os.path.join(
                    temp_passport_path,
                    str(base_social_worker.id) + '-passport_' + filename2,
                )

                file2.save(base_social_worker.passportUrl)

                base_social_worker.passportUrl = '/' + base_social_worker.passportUrl
            else:
                return {'message': 'invalid passport file!'}, 400

        if 'avatarUrl' in request.files.keys():
            file3 = request.files['avatarUrl']

            if file3.filename == '':
                return {'message': 'ERROR OCCURRED --> EMPTY Avatar!'}, 400

            if extension := valid_image_extension(file3):
                filename3 = base_social_worker.generatedCode + uuid4().hex + extension

                temp_avatar_path = os.path.join(
                    configs.UPLOAD_FOLDER,
                    str(base_social_worker.id) + '-socialworker',
                )

                if not os.path.isdir(temp_avatar_path):
                    os.makedirs(temp_avatar_path, exist_ok=True)

                for obj in os.listdir(temp_avatar_path):
                    check = str(base_social_worker.id) + '-avatar'
                    if obj.split('_')[0] == check:
                        os.remove(os.path.join(temp_avatar_path, obj))

                base_social_worker.avatarUrl = os.path.join(
                    temp_avatar_path,
                    str(base_social_worker.id) + '-avatar_' + filename3,
                )

                file3.save(base_social_worker.avatarUrl)
                base_social_worker.avatarUrl = '/' + base_social_worker.avatarUrl
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
            base_social_worker.password = request.form['password']

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
