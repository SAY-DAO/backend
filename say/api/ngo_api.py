import os
from datetime import datetime

from flasgger import swag_from
from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename

from say.api.ext import api
from say.authorization import authorize
from say.config import configs
from say.decorators import json
from say.exceptions import HTTP_NOT_FOUND
from say.models import obj_to_dict
from say.models.ngo_model import Ngo
from say.models.social_worker_model import SocialWorker
from say.orm import safe_commit
from say.orm import session
from say.roles import *
from say.validations import allowed_image


'''
Activity APIs
'''


def sw_list(social_worker_list):
    res = {}
    for sw in social_worker_list:
        res[str(sw.id)] = obj_to_dict(sw)

    return res


class GetAllNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/all.yml')
    def get(self):
        base_ngos = session.query(Ngo).filter_by(isDeleted=False).all()

        fetch = {}
        for n in base_ngos:
            data = obj_to_dict(n)

            data['coordinator'] = obj_to_dict(n.coordinator)
            fetch[str(n.id)] = data

        return fetch


class AddNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/add.yml')
    def post(self):
        if len(session.query(Ngo).all()):
            last_ngo = session.query(Ngo).order_by(Ngo.id.desc()).first()
            current_id = last_ngo.id + 1
        else:
            current_id = 1

        path = 'some wrong url'
        if 'logoUrl' not in request.files:
            return {'message': 'ERROR OCCURRED IN FILE UPLOADING!'}, 400

        file = request.files['logoUrl']
        if file.filename == '':
            return {'message': 'ERROR OCCURRED --> EMPTY FILE!'}, 400

        if file and allowed_image(file.filename):
            filename = secure_filename(file.filename)
            filename = (
                    format(current_id, '03d') + '.' + filename.split('.')[-1]
            )

            temp_logo_path = os.path.join(
                configs.UPLOAD_FOLDER, str(current_id) + '-ngo'
            )

            if not os.path.isdir(temp_logo_path):
                os.makedirs(temp_logo_path, exist_ok=True)

            path = os.path.join(
                temp_logo_path, str(current_id) + '-logo_' + filename
            )

            file.save(path)
            path = '/' + path

        logo_url = path
        country = int(request.form['country'])
        city = int(request.form['city'])
        try:
            coordinator_id = request.form.get('coordinatorId')
            if coordinator_id:
                coordinator_id = int(coordinator_id)
        except (ValueError, TypeError):
            return {'message': 'invalid coordinatorId'}, 400

        name = request.form['name']
        postal_address = request.form['postalAddress']
        email_address = request.form['emailAddress']
        phone_number = request.form['phoneNumber']
        if 'balance' in request.form.keys():
            balance = request.form['balance']
        else:
            balance = 0

        if 'website' in request.form.keys():
            website = request.form['website']
        else:
            website = None

        register_date = datetime.utcnow()

        new_ngo = Ngo(
            name=name,
            country=country,
            city=city,
            coordinatorId=coordinator_id,
            postalAddress=postal_address,
            emailAddress=email_address,
            phoneNumber=phone_number,
            logoUrl=logo_url,
            balance=balance,
            registerDate=register_date,
            website=website,
        )

        session.add(new_ngo)
        safe_commit(session)
        return new_ngo


class GetNgoById(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/id.yml')
    def get(self, ngo_id):
        base_ngo = session.query(Ngo) \
            .filter_by(id=ngo_id) \
            .filter_by(isDeleted=False) \
            .one_or_none()

        if not base_ngo:
            return {'message': 'sth went wrong!'}, 400

        res = obj_to_dict(base_ngo)
        res['coordinatorFirstName'] = None
        res['coordinatorLastName'] = None

        if base_ngo.coordinatorId:
            coordinator = session.query(
                SocialWorker.firstName,
                SocialWorker.lastName,
            ) \
                .filter_by(id=base_ngo.coordinatorId) \
                .filter_by(isDeleted=False) \
                .one_or_none()

            res['coordinatorFirstName'] = coordinator[0]
            res['coordinatorLastName'] = coordinator[1]

        res['socialWorkers'] = sw_list(session.query(SocialWorker)
            .filter_by(id_ngo=base_ngo.id)
            .filter_by(isDeleted=False)
            .all()
        )
        return res


class UpdateNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/update.yml')
    def patch(self, ngo_id):
        base_ngo = session.query(Ngo) \
            .filter_by(id=ngo_id) \
            .filter_by(isDeleted=False) \
            .one_or_none()

        if base_ngo is None:
            raise HTTP_NOT_FOUND()

        if 'country' in request.form.keys():
            base_ngo.country = int(request.form['country'])

        if 'city' in request.form.keys():
            base_ngo.city = int(request.form['city'])

        if 'coordinatorId' in request.form.keys():
            base_ngo.coordinatorId = int(request.form['coordinatorId'])

        if 'name' in request.form.keys():
            base_ngo.name = request.form['name']

        if 'website' in request.form.keys():
            base_ngo.website = request.form['website']

        if 'postalAddress' in request.form.keys():
            base_ngo.postalAddress = request.form['postalAddress']

        if 'emailAddress' in request.form.keys():
            base_ngo.emailAddress = request.form['emailAddress']

        if 'phoneNumber' in request.form.keys():
            base_ngo.phoneNumber += ',' + str(request.form['phoneNumber'])

        if 'balance' in request.form.keys():
            base_ngo.balance = request.form['balance']

        if 'logoUrl' in request.files.keys():
            file = request.files['logoUrl']

            if file.filename == '':
                return {'message': 'ERROR OCCURRED --> EMPTY FILE!'}, 400

            if file and allowed_image(file.filename):
                filename = secure_filename(file.filename)
                filename = (
                        format(base_ngo.id, '03d') + '.' +
                        filename.split('.')[-1]
                )
                temp_logo_path = os.path.join(
                    configs.UPLOAD_FOLDER, str(base_ngo.id) + '-ngo'
                )

                if not os.path.isdir(temp_logo_path):
                    os.makedirs(temp_logo_path, exist_ok=True)

                for obj in os.listdir(temp_logo_path):
                    check = str(base_ngo.id) + '-logo'

                    if obj.split('_')[0] == check:
                        os.remove(os.path.join(temp_logo_path, obj))

                base_ngo.logoUrl = os.path.join(
                    temp_logo_path, str(base_ngo.id) + '-logo_' + filename
                )

                file.save(base_ngo.logoUrl)
                base_ngo.logoUrl = '/' + base_ngo.logoUrl

        safe_commit(session)
        return base_ngo


class DeleteNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/delete.yml')
    def patch(self, ngo_id):
        base_ngo = session.query(Ngo) \
            .filter_by(id=ngo_id) \
            .filter_by(isDeleted=False) \
            .one_or_none()

        if base_ngo is None:
            raise HTTP_NOT_FOUND()

        base_ngo.isDeleted = True

        safe_commit(session)
        return {'message': 'ngo deleted successfully!'}


class DeactivateNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/deactivate.yml')
    def patch(self, ngo_id):
        base_ngo = session.query(Ngo) \
            .filter_by(id=ngo_id) \
            .filter_by(isActive=True) \
            .filter_by(isDeleted=False) \
            .one_or_none()

        if base_ngo is None:
            raise HTTP_NOT_FOUND()

        base_ngo.isActive = False
        safe_commit(session)
        return base_ngo


class ActivateNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/activate.yml')
    def patch(self, ngo_id):
        base_ngo = session.query(Ngo) \
            .filter_by(id=ngo_id) \
            .filter_by(isActive=False) \
            .filter_by(isDeleted=False) \
            .one_or_none()

        if base_ngo is None:
            raise HTTP_NOT_FOUND()

        base_ngo.isActive = True

        safe_commit(session)
        return base_ngo


api.add_resource(GetAllNgo, '/api/v2/ngo/all')
api.add_resource(AddNgo, '/api/v2/ngo/add')
api.add_resource(GetNgoById, '/api/v2/ngo/ngoId=<ngo_id>')
api.add_resource(UpdateNgo, '/api/v2/ngo/update/ngoId=<ngo_id>')
api.add_resource(DeleteNgo, '/api/v2/ngo/delete/ngoId=<ngo_id>')
api.add_resource(DeactivateNgo, '/api/v2/ngo/deactivate/ngoId=<ngo_id>')
api.add_resource(ActivateNgo, '/api/v2/ngo/activate/ngoId=<ngo_id>')
