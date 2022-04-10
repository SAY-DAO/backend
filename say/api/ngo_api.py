import os
from datetime import datetime
from uuid import uuid4

from flasgger import swag_from
from flask import request
from flask_restful import Resource

from say.api.ext import api
from say.authorization import authorize
from say.config import configs
from say.decorators import json
from say.exceptions import HTTP_NOT_FOUND
from say.models import City
from say.models import obj_to_dict
from say.models.ngo_model import Ngo
from say.models.social_worker_model import SocialWorker
from say.orm import safe_commit
from say.orm import session
from say.roles import *
from say.validations import valid_image_extension

from ..exceptions import HTTP_BAD_REQUEST


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
        base_ngos = session.query(Ngo).filter_by(isDeleted=False)
        return base_ngos


class AddNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/add.yml')
    def post(self):
        if 'logoUrl' not in request.files:
            return {'message': 'Logo is required!'}, 400

        logo_file = request.files['logoUrl']
        if extension := valid_image_extension(logo_file):
            logo_name = uuid4().hex + extension
            logo_path = os.path.join(configs.UPLOAD_FOLDER, 'ngos/logos')

            if not os.path.isdir(logo_path):
                os.makedirs(logo_path, exist_ok=True)

            logo = os.path.join(logo_path, logo_name)
            logo_file.save(logo)
        else:
            return {'message': 'invalid image file!'}, 400

        city_id = request.form.get('cityId', None)

        if city_id:
            try:
                city_id = int(city_id)
            except (ValueError, TypeError):
                raise HTTP_BAD_REQUEST(message='cityId should be integer')

            city = (
                session.query(City)
                .filter(City.id == city_id)
                .populate_existing()
                .with_for_update()
                .one_or_none()
            )

            if city is None:
                raise HTTP_BAD_REQUEST(message='city not found')
        else:
            raise HTTP_BAD_REQUEST(message='cityId is required')

        if 'name' not in request.form.keys():
            raise HTTP_BAD_REQUEST(message='name is required')

        if 'postalAddress' not in request.form.keys():
            raise HTTP_BAD_REQUEST(message='postalAddress is required')

        if 'emailAddress' not in request.form.keys():
            raise HTTP_BAD_REQUEST(message='emailAddress is required')

        if 'phoneNumber' not in request.form.keys():
            raise HTTP_BAD_REQUEST(message='phoneNumber is required')

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
            city_id=city_id,
            postalAddress=postal_address,
            emailAddress=email_address,
            phoneNumber=phone_number,
            logoUrl=logo,
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
        base_ngo = (
            session.query(Ngo)
            .filter_by(id=ngo_id)
            .filter_by(isDeleted=False)
            .one_or_none()
        )

        if not base_ngo:
            return {'message': 'sth went wrong!'}, 400

        res = obj_to_dict(base_ngo)

        res['socialWorkers'] = sw_list(
            session.query(SocialWorker)
            .filter_by(ngo_id=base_ngo.id)
            .filter_by(is_deleted=False)
            .all()
        )
        return res


class UpdateNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/update.yml')
    def patch(self, ngo_id):
        base_ngo = (
            session.query(Ngo)
            .filter_by(id=ngo_id)
            .filter_by(isDeleted=False)
            .one_or_none()
        )

        if base_ngo is None:
            raise HTTP_NOT_FOUND()

        if 'cityId' in request.form.keys():
            city_id = request.form['cityId']
            try:
                city_id = int(city_id)
            except (ValueError, TypeError):
                raise HTTP_BAD_REQUEST(message='cityId should be integer')

            city = (
                session.query(City)
                .filter(City.id == city_id)
                .populate_existing()
                .with_for_update()
                .one_or_none()
            )

            if city is None:
                raise HTTP_BAD_REQUEST(message='city not found')

            base_ngo.city_id = city_id
        else:
            raise HTTP_BAD_REQUEST(message='cityId is required')
            
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
            logo_file = request.files['logoUrl']
            if extension := valid_image_extension(logo_file):
                logo_name = uuid4().hex + extension
                logo_path = os.path.join(configs.UPLOAD_FOLDER, 'ngos/logos')

                if not os.path.isdir(logo_path):
                    os.makedirs(logo_path, exist_ok=True)

                logo = os.path.join(logo_path, logo_name)
                logo_file.save(logo)
                base_ngo.logoUrl = logo
            else:
                return {'message': 'invalid image file!'}, 400

        safe_commit(session)
        return base_ngo


class DeleteNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/ngo/delete.yml')
    def patch(self, ngo_id):
        base_ngo = (
            session.query(Ngo)
            .filter_by(id=ngo_id)
            .filter_by(isDeleted=False)
            .one_or_none()
        )

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
        base_ngo = (
            session.query(Ngo)
            .filter_by(id=ngo_id)
            .filter_by(isActive=True)
            .filter_by(isDeleted=False)
            .one_or_none()
        )

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
        base_ngo = (
            session.query(Ngo)
            .filter_by(id=ngo_id)
            .filter_by(isActive=False)
            .filter_by(isDeleted=False)
            .one_or_none()
        )

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
