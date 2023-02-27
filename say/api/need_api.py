import os
from collections import OrderedDict
from datetime import datetime
from uuid import uuid4

import ujson
from flasgger import swag_from
from flask import request
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload

from say.api.ext import api
from say.authorization import authorize
from say.authorization import get_sw_ngo_id
from say.authorization import get_user_id
from say.authorization import get_user_role
from say.config import configs
from say.constants import CATEGORIES
from say.constants import DEFAULT_CHILD_ID
from say.date import parse_date
from say.decorators import json
from say.decorators import validate
from say.exceptions import HTTP_BAD_REQUEST
from say.exceptions import HTTP_NOT_FOUND
from say.exceptions import HTTP_PERMISION_DENIED
from say.models import commit
from say.models import obj_to_dict
from say.models.child_model import Child
from say.models.child_need_model import ChildNeed
from say.models.family_model import Family
from say.models.need_model import Need
from say.models.need_status_update import NeedStatusUpdate
from say.models.receipt import NeedReceipt
from say.models.receipt import Receipt
from say.models.social_worker_model import SocialWorker
from say.models.user_family_model import UserFamily
from say.orm import safe_commit
from say.orm import session
from say.roles import ADMIN
from say.roles import COORDINATOR
from say.roles import NGO_SUPERVISOR
from say.roles import SAY_SUPERVISOR
from say.roles import SOCIAL_WORKER
from say.roles import SUPER_ADMIN
from say.roles import USER
from say.schema import NewReceiptSchema
from say.schema import ReceiptSchema
from say.schema.base import PaginationSchema
from say.schema.need import AllNeedQuerySchema
from say.validations import valid_image_extension

from . import *


'''
Need APIs
'''


def filter_by_privilege(query, get=False):  # TODO: priv
    user_role = get_user_role()
    user_id = get_user_id()
    ngo_id = get_sw_ngo_id()

    if user_role in [SOCIAL_WORKER, COORDINATOR]:
        if get:
            query = query.join(Child).filter(
                or_(Child.id_social_worker == user_id, Child.id == 104)
            )
        else:
            query = query.join(Child).filter(Child.id_social_worker == user_id)

    elif user_role in [NGO_SUPERVISOR]:
        if get:
            query = (
                query.join(Child)
                .join(SocialWorker)
                .filter(or_(SocialWorker.ngo_id == ngo_id, Child.id == 104))
            )
        else:
            query = (
                query.join(Child).join(SocialWorker).filter(SocialWorker.ngo_id == ngo_id)
            )

    elif user_role in [USER]:
        query = (
            query.join(Child)
            .join(Family)
            .join(UserFamily)
            .filter(UserFamily.id_user == user_id)
            .filter(UserFamily.isDeleted.is_(False))
        )

    return query


class ListNeeds(Resource):
    @authorize(
        SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @validate(AllNeedQuerySchema)
    @json
    @swag_from('./docs/need/all.yml')
    def get(self, data: AllNeedQuerySchema):
        sw_role = get_user_role()

        needs = (
            session.query(Need)
            .filter(Need.isDeleted.is_(False))
            .order_by(Need.created.desc())
        )

        if data.is_confirmed is not None:
            needs = needs.filter_by(isConfirmed=data.is_confirmed)

        if data.is_done is not None:
            needs = needs.filter_by(isDone=data.is_done)

        if data.type is not None:
            needs = needs.filter_by(type=data.type)

        if data.status is not None:
            needs = needs.filter_by(status=data.status)

        if data.is_reported is not None:
            needs = needs.filter_by(isReported=data.is_reported)

        if data.created_by is not None:
            needs = needs.filter(Need.created_by_id == data.created_by)

        if data.confirmed_by is not None:
            needs = needs.filter(Need.confirmUser == data.confirmed_by)

        if data.purchased_by is not None:
            needs = (
                needs.join(
                    NeedStatusUpdate,
                    Need.id == NeedStatusUpdate.need_id,
                )
                .filter(
                    NeedStatusUpdate.sw_id == data.purchased_by,
                    NeedStatusUpdate.new_status == 3,
                    NeedStatusUpdate.old_status == 2,
                )
                .distinct()
            )

        if data.unpayable is not None:
            needs = needs.filter(
                Need.unpayable == data.unpayable,
                Need.status.in_((0, 1, 2, 3)),
                Need.isConfirmed.is_(True),
            )

        if data.is_child_confirmed is not None:
            children_id = session.query(Child.id).filter(
                Child.isConfirmed == data.is_child_confirmed,
            )
            needs = needs.filter(Need.child_id.in_(children_id))

        if data.ngo_id and sw_role in [SUPER_ADMIN, SAY_SUPERVISOR, ADMIN]:
            needs = needs.join(Child).filter(Child.id_ngo == data.ngo_id)

        needs = filter_by_privilege(needs)
        all_needs_count = needs.count()

        pagination = PaginationSchema.parse_obj(request.headers)
        if pagination.take:
            needs = needs.limit(pagination.take)
        else:
            needs = needs.limit(25)

        if pagination.skip:
            needs = needs.offset(pagination.skip)

        need_count = needs.count()

        if sw_role in [
            SOCIAL_WORKER,
            COORDINATOR,
            NGO_SUPERVISOR,
            SUPER_ADMIN,
            SAY_SUPERVISOR,
            ADMIN,
        ]:
            needs = needs.options(selectinload(Need.payments))

        needs = needs.options(selectinload(Need.child)).options(selectinload('child.ngo'))
        result = OrderedDict(
            all_needs_count=all_needs_count,
            totalCount=need_count,
            needs=[],
        )
        for need in needs:
            res = obj_to_dict(need)

            ngo = need.child.ngo
            child = need.child

            res['ngoId'] = ngo.id
            res['ngoName'] = ngo.name
            res['ngoAddress'] = ngo.postalAddress
            res['childGeneratedCode'] = child.generatedCode
            res['childFirstName'] = child.firstName
            res['childLastName'] = child.lastName
            res['childSayName'] = child.sayName

            if sw_role in [
                SOCIAL_WORKER,
                COORDINATOR,
                NGO_SUPERVISOR,
                SUPER_ADMIN,
                SAY_SUPERVISOR,
                ADMIN,
            ]:
                res['payments'] = obj_to_dict(need.payments)

            result['needs'].append(res)

        return result


class GetNeedById(Resource):
    @authorize(
        SOCIAL_WORKER,
        COORDINATOR,
        NGO_SUPERVISOR,
        SUPER_ADMIN,
        SAY_SUPERVISOR,
        ADMIN,
        USER,
    )  # TODO: priv
    @json
    @swag_from('./docs/need/id.yml')
    def get(self, need_id):
        need_query = (
            session.query(Need)
            .options(joinedload(Need.participants))
            .filter_by(isDeleted=False)
            .filter_by(id=need_id)
        )

        need = filter_by_privilege(need_query, get=True).one_or_none()

        if need is None:
            raise HTTP_NOT_FOUND()

        need_dict = obj_to_dict(need)

        need_dict['participants'] = [
            obj_to_dict(p, proxys=True) for p in need.current_participants
        ]
        return need_dict


class UpdateNeedById(Resource):
    @authorize(
        SOCIAL_WORKER,
        COORDINATOR,
        NGO_SUPERVISOR,
        SUPER_ADMIN,
        SAY_SUPERVISOR,
        ADMIN,
    )  # TODO: priv
    @json
    @swag_from('./docs/need/update.yml')
    def patch(self, need_id):
        sw_role = get_user_role()

        need_query = (
            session.query(Need)
            .filter_by(id=need_id)
            .filter_by(isDeleted=False)
            .with_for_update()
        )

        need = filter_by_privilege(need_query).one_or_none()

        if need is None:
            raise HTTP_NOT_FOUND()

        child = need.child
        temp_need_path = os.path.join(configs.UPLOAD_FOLDER, str(child.id) + '-child')
        temp_need_path = os.path.join(temp_need_path, 'needs')
        temp_need_path = os.path.join(temp_need_path, str(need.id) + '-need')

        if not os.path.isdir(temp_need_path):
            os.makedirs(temp_need_path, exist_ok=True)

        if need.isConfirmed and sw_role not in (ADMIN, SUPER_ADMIN, SAY_SUPERVISOR):
            safe_commit(session)
            need_dict = obj_to_dict(need)
            return need_dict

        if 'cost' in request.form.keys():
            new_cost = int(request.form['cost'].replace(',', ''))

            if (
                (
                    sw_role in [SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR]
                    and need.isConfirmed
                )
                or need.isDone
            ) and new_cost != need._cost:
                return {'message': 'Can not change cost when need is done'}, 400

            need.cost = new_cost

        if 'imageUrl' in request.files.keys():
            image_file = request.files['imageUrl']
            if extension := valid_image_extension(image_file):
                filename = uuid4().hex + extension
                need.imageUrl = os.path.join(temp_need_path, filename)
                image_file.save(need.imageUrl)
            else:
                return {'message': 'invalid image file!'}, 400

        if 'category' in request.form.keys():
            need.category = int(request.form['category'])

        if 'type' in request.form.keys():
            need.type = int(request.form['type'])

        if 'isUrgent' in request.form.keys():
            need.isUrgent = True if request.form['isUrgent'] == 'true' else False

        if 'link' in request.form.keys():
            new_link = request.form['link']
            if new_link != need.link:
                from say.tasks import update_need

                need.link = new_link
                session.flush()
                update_need.delay(need.id, force=True)

        if 'affiliateLinkUrl' in request.form.keys():
            need.affiliateLinkUrl = request.form['affiliateLinkUrl']

        if 'name_translations' in request.form.keys():
            need.name_translations = ujson.loads(
                request.form['name_translations'],
            )

        if 'description_translations' in request.form.keys():
            need.description_translations = ujson.loads(
                request.form['description_translations'],
            )

        if 'doing_duration' in request.form.keys():
            need.doing_duration = int(request.form['doing_duration'])

        if 'details' in request.form.keys():
            need.details = request.form['details']

        if 'informations' in request.form.keys():
            need.informations = request.form['informations']

        if dkc := request.form.get('dkc'):
            need.dkc = dkc

        if request.form.get('expected_delivery_date'):
            if not (2 <= need.status <= 3):
                raise Exception('Expected delivery date can not changed in this status')

            need.isReported = False
            need.expected_delivery_date = parse_date(
                request.form['expected_delivery_date']
            )

        prev_status = need.status

        if 'status' in request.form.keys():
            new_status = int(request.form['status'])

            purchase_cost = request.form.get('purchase_cost', None)
            if (
                purchase_cost
                and sw_role in [SUPER_ADMIN, SAY_SUPERVISOR, ADMIN]
                and (
                    (new_status == 3 and need.type == 1)
                    or (new_status == 4 and need.type == 0)
                )
            ):

                purchase_cost = purchase_cost.replace(',', '')
                need.purchase_cost = int(purchase_cost)
                if need.purchase_date is not None:
                    need.oncePurchased = True

            if new_status != 5 and new_status - prev_status == 1:
                if new_status == 4 and need.isReported is not True:
                    return {'message': 'Need has not been reported to ngo yet'}, 400

                if new_status == 4 and need.type == 0 and len(need.receipts_) == 0:
                    return (
                        {
                            'message': 'There is not receipt for this need, '
                            'please upload related receipt before changing the status.'
                        },
                        400,
                    )

                session.flush()
                need_status = NeedStatusUpdate(
                    sw_id=get_user_id(),
                    new_status=new_status,
                    old_status=need.status,
                    need_id=need.id,
                )
                need.status = new_status
                need.status_updates.append(need_status)

            elif new_status != prev_status:
                return (
                    {
                        'message': f'Can not change status from '
                        f'{prev_status} to {new_status}',
                    },
                    400,
                )

        if need.type == 0 and need.status == 3:
            bank_track_id = request.form.get('bank_track_id')

            if not bank_track_id and prev_status == 2:
                raise ValueError('bank_track_id is required')

            if bank_track_id:
                need.bank_track_id = bank_track_id

        safe_commit(session)
        return need


class DeleteNeedById(Resource):
    @json
    @commit
    @authorize(
        SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @swag_from('./docs/need/delete.yml')
    def patch(self, need_id):
        need = session.query(Need).filter_by(isDeleted=False).filter_by(id=need_id)

        need = filter_by_privilege(need).with_for_update().one_or_none()
        if not need:
            return {'message': 'need not found'}, 404

        if (
            get_user_role() in (SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR)
            and need.isConfirmed
        ):
            return {'message': 'permision denied'}, 403

        if (need.type == 0 and need.status < 4) or (need.type == 1 and need.status < 5):
            need.delete()
            return {'message': 'need deleted'}
        else:
            return {'message': 'need has arrived to the child so can not be deleted'}, 422


class ConfirmNeed(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/need/confirm.yml')
    def patch(self, need_id):
        social_worker_id = get_user_id()

        primary_need = (
            session.query(Need)
            .filter_by(id=need_id)
            .filter_by(isDeleted=False)
            .one_or_none()
        )

        if primary_need is None:
            return {'message': 'need not found'}, 404

        if primary_need.isConfirmed:
            return {'message': 'need has already been confirmed!'}, 400

        if primary_need.category not in CATEGORIES:
            return {'message': 'Invalid category'}, 400

        if (
            not primary_need.description_translations['en']
            or not primary_need.description_translations['fa']
        ):
            return {'message': 'Invalid description translations'}, 400

        if not primary_need.name_translations['en']:
            return {'message': 'Invalid name translations'}, 400

        child = primary_need.child

        primary_need.isConfirmed = True
        primary_need.confirmUser = social_worker_id
        primary_need.confirmDate = datetime.utcnow()

        new_child_need = ChildNeed(
            id_child=child.id,
            id_need=primary_need.id,
        )

        child.social_worker.need_count += 1
        child.social_worker.current_need_count += 1

        session.add(new_child_need)
        safe_commit(session)

        return {'message': 'need confirmed successfully!'}


class UnconfirmNeed(Resource):
    @json
    @commit
    @authorize(
        SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @swag_from('./docs/need/unconfirm.yml')
    def post(self, id):
        need = session.query(Need).filter_by(isDeleted=False).filter_by(id=id)
        need = filter_by_privilege(need).with_for_update().one_or_none()

        if not need:
            return {'message': 'need not found'}, 404

        if not need.isConfirmed:
            return {'message': 'need is not confirmed'}, 600

        if (
            get_user_role() in (SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR)
            and need.status > 0
        ):
            return {'message': 'permission denied'}, 403

        if (need.type == 0 and need.status >= 3) or (need.type == 1 and need.status >= 4):
            return {
                'message': f'need with status {need.status} cannot be unconfirmed'
            }, 601

        need.unconfirm()
        return need


class AddNeed(Resource):
    def check_privilege(self, sw_id, allowed_sw_ids):  # TODO: priv
        sw_role = get_user_role()

        if sw_role in [SOCIAL_WORKER, COORDINATOR]:
            if sw_id != get_user_id():
                raise HTTP_PERMISION_DENIED()

        elif sw_role in [NGO_SUPERVISOR]:
            if sw_id not in allowed_sw_ids:
                raise HTTP_PERMISION_DENIED()

        return None

    @authorize(
        SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @json
    @swag_from('./docs/need/add.yml')
    def post(self):
        child_id = int(request.form['child_id'])
        child = (
            session.query(Child)
            .filter_by(id=child_id)
            .filter_by(isDeleted=False)
            .filter_by(isMigrated=False)
            .filter_by(isConfirmed=True)
            .one_or_none()
        )

        if child is None:
            return {'message': 'error: child not found!'}, 400

        sw_id = int(request.form.get('sw_id', get_user_id()))
        sw_role = get_user_role()

        allowed_sw_ids = []
        if sw_role in [NGO_SUPERVISOR]:
            allowed_sw_ids_tuple = (
                session.query(SocialWorker.id)
                .filter_by(is_deleted=False)
                .filter_by(ngo_id=get_sw_ngo_id())
                .distinct()
                .all()
            )

            allowed_sw_ids = [item[0] for item in allowed_sw_ids_tuple]

        # May throw
        self.check_privilege(sw_id, allowed_sw_ids)

        if not child.isConfirmed:
            return {'message': 'error: child is not confirmed yet!'}, 400

        image_path = 'wrong path'

        image_url = image_path

        category = request.form.get('category')
        if not category:
            return {'message': 'error: category is required!'}, 400

        try:
            category = int(request.form['category'])
        except ValueError:
            return {'message': 'error: category should be integer!'}, 400

        if category not in CATEGORIES:
            return {'message': f'error: category should be {CATEGORIES}'}, 400

        cost = request.form['cost'].replace(',', '')

        name_translations = ujson.loads(request.form['name_translations'])
        description_translations = ujson.loads(
            request.form['description_translations'],
        )

        is_urgent = True if request.form['isUrgent'] == 'true' else False
        need_type = request.form['type']

        details = request.form.get('details', '')
        link = request.form.get('link', None)

        if 'affiliateLinkUrl' in request.form.keys():
            affiliate_link_url = request.form['affiliateLinkUrl']
        else:
            affiliate_link_url = None

        if 'doing_duration' in request.form.keys():
            doing_duration = int(request.form['doing_duration'])
        else:
            doing_duration = 5

        new_need = Need(
            created_by_id=sw_id,
            name_translations=name_translations,
            description_translations=description_translations,
            imageUrl=image_url,
            category=category,
            cost=cost,
            isUrgent=is_urgent,
            affiliateLinkUrl=affiliate_link_url,
            link=link,
            type=need_type,
            child=child,
            doing_duration=doing_duration,
            details=details,
            informations=request.form.get('informations', ''),
        )
        session.add(new_need)
        session.flush()

        child_path = os.path.join(
            configs.UPLOAD_FOLDER,
            str(child.id) + '-child',
        )
        needs_path = os.path.join(child_path, 'needs')
        if not os.path.isdir(child_path):
            os.makedirs(child_path, exist_ok=True)

        if not os.path.isdir(needs_path):
            os.makedirs(needs_path, exist_ok=True)

        need_dir = str(new_need.id) + '-need'
        need_path = os.path.join(needs_path, need_dir)

        if 'imageUrl' in request.files:
            image_file = request.files['imageUrl']
            if extension := valid_image_extension(image_file):
                image_name = uuid4().hex + extension
                if not os.path.isdir(need_path):
                    os.makedirs(need_path, exist_ok=True)

                new_need.imageUrl = os.path.join(need_path, image_name)
                image_file.save(new_need.imageUrl)
            else:
                return {'message': 'Invalid image'}, 400

        safe_commit(session)

        if new_need.link:
            from say.tasks import update_need

            update_need.delay(new_need.id)

        return new_need


class NeedReceipts(Resource):
    @json
    @swag_from('./docs/need/list_receipts.yml')
    def get(self, id):
        try:
            user_role = get_user_role()
            user_id = get_user_id()
            ngo_id = get_sw_ngo_id()
        except NoAuthorizationError:
            user_role = None
            user_id = None
            ngo_id = None

        base_query = (
            session.query(Receipt)
            .join(NeedReceipt, NeedReceipt.receipt_id == Receipt.id)
            .join(Need, NeedReceipt.need_id == Need.id)
            .join(Child, Child.id == Need.child_id)
            .join(SocialWorker, SocialWorker.id == Child.id_social_worker)
            .filter(
                Need.isDeleted.is_(False),
                Receipt.deleted.is_(None),
                NeedReceipt.deleted.is_(None),
                Need.id == id,
                or_(
                    True if user_role in [SUPER_ADMIN, ADMIN, SAY_SUPERVISOR] else False,
                    Receipt.is_public.is_(True),
                    Receipt.owner_id == user_id
                    if user_role not in [SUPER_ADMIN, ADMIN, SAY_SUPERVISOR]
                    else False,
                    SocialWorker.ngo_id == ngo_id
                    if user_role in [NGO_SUPERVISOR]
                    else False,
                ),
            )
        )

        res = []
        for r in base_query:
            res.append(ReceiptSchema.from_orm(r))

        return res

    @authorize(
        SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )
    @json(ReceiptSchema)
    @swag_from('./docs/need/new_receipt.yml')
    def post(self, id):
        sw_id = get_user_id()

        try:
            data = NewReceiptSchema(
                **request.form.to_dict(),
                **request.files,
                owner_id=sw_id,
            )
        except ValueError as e:
            return e.json(), 400

        need = filter_by_privilege(
            session.query(Need).filter(
                Need.id == id,
                Need.isDeleted.is_(False),
            )
        ).one_or_none()

        if need is None:
            raise HTTP_NOT_FOUND()

        if data.need_status and need.status < data.need_status:
            raise HTTP_BAD_REQUEST(
                message='needStatus should be lower than current need status',
            )

        receipt = Receipt(**data.dict())
        need_receipt = NeedReceipt(
            need=need,
            receipt=receipt,
            sw_id=sw_id,
        )
        session.add(need_receipt)

        data.attachment.save(data.attachment.filepath)
        receipt.attachment = data.attachment.filepath

        safe_commit(session)
        return receipt


class NeedReceiptAPI(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @json(ReceiptSchema)
    @swag_from('./docs/need/delete_receipt.yml')
    def delete(self, id, receiptId):
        receipt_id = receiptId
        need_receipt = (
            session.query(NeedReceipt)
            .filter(
                NeedReceipt.need_id == id,
                NeedReceipt.receipt_id == receipt_id,
                NeedReceipt.deleted.is_(None),
            )
            .one_or_none()
        )

        if need_receipt is None:
            raise HTTP_NOT_FOUND()

        need_receipt.deleted = datetime.utcnow()
        safe_commit(session)
        return need_receipt.receipt


"""
API URLs
"""

api.add_resource(GetNeedById, '/api/v2/need/needId=<int:need_id>')
api.add_resource(ListNeeds, '/api/v2/needs')
api.add_resource(UpdateNeedById, '/api/v2/need/update/needId=<int:need_id>')
api.add_resource(DeleteNeedById, '/api/v2/need/delete/needId=<int:need_id>')
api.add_resource(ConfirmNeed, '/api/v2/need/confirm/needId=<int:need_id>')
api.add_resource(UnconfirmNeed, '/api/v2/needs/<int:id>/unconfirm')
api.add_resource(AddNeed, '/api/v2/need/')
api.add_resource(NeedReceipts, '/api/v2/needs/<int:id>/receipts')
api.add_resource(NeedReceiptAPI, '/api/v2/needs/<int:id>/receipts/<int:receiptId>')
