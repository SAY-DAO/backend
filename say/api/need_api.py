import os
from collections import OrderedDict
from datetime import datetime
from uuid import uuid4

import ujson
from flasgger import swag_from
from flask import request
from flask_restful import Resource
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from say.api.ext import api
from say.authorization import authorize
from say.authorization import get_sw_ngo_id
from say.authorization import get_user_id
from say.authorization import get_user_role
from say.config import configs
from say.constants import DEFAULT_CHILD_ID
from say.date import parse_datetime
from say.decorators import json
from say.exceptions import HTTP_NOT_FOUND
from say.exceptions import HTTP_PERMISION_DENIED
from say.models import commit
from say.models import obj_to_dict
from say.models.child_model import Child
from say.models.child_need_model import ChildNeed
from say.models.family_model import Family
from say.models.need_family_model import NeedFamily
from say.models.need_model import Need
from say.models.receipt import NeedReceipt
from say.models.receipt import Receipt
from say.models.social_worker_model import SocialWorker
from say.models.user_family_model import UserFamily
from say.orm import safe_commit
from say.orm import session
from say.roles import *
from say.schema import NewReceiptSchema
from say.schema import ReceiptSchema
from say.validations import allowed_image
from say.validations import allowed_receipt

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
            query = query.join(Child).filter(or_(
                Child.id_social_worker == user_id,
                Child.id == DEFAULT_CHILD_ID,
            ))
        else:
            query = query.join(Child).filter(Child.id_social_worker == user_id)

    elif user_role in [NGO_SUPERVISOR]:
        if get:
            query = query \
                .join(Child) \
                .join(SocialWorker) \
                .filter(or_(
                    SocialWorker.id_ngo == ngo_id,
                    Child.id == DEFAULT_CHILD_ID,
                ))
        else:
            query = query \
                .join(Child) \
                .join(SocialWorker) \
                .filter(SocialWorker.id_ngo == ngo_id)

    elif user_role in [USER]:
        query = query \
            .join(Child) \
            .join(Family) \
            .join(UserFamily) \
            .filter(UserFamily.id_user == user_id) \
            .filter(UserFamily.isDeleted.is_(False))

    return query


class GetAllNeeds(Resource):

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/need/all.yml')
    def get(self, confirm):
        sw_role = get_user_role()
        args = request.args
        done = args.get('done', -1)
        status = args.get('status', None)
        ngo_id = args.get('ngoId', None)

        is_reported = args.get('isReported', None)
        type_ = args.get('type', None)

        done = int(done)
        needs = session.query(Need) \
            .filter(Need.isDeleted.is_(False)) \
            .order_by(Need.doneAt.desc())

        if int(confirm) == 1:
            needs = (
                needs
                    .filter_by(isDeleted=False)
                    .filter_by(isConfirmed=True)
            )

        elif int(confirm) == 0:
            needs = (
                needs
                    .filter_by(isDeleted=False)
                    .filter_by(isConfirmed=False)
            )

        if done == 1:
            needs = needs.filter_by(isDone=True)

        elif done == 0:
            needs = needs.filter_by(isDone=False)

        if type_:
            type_ = int(type_)
            needs = needs.filter_by(type=type_)

        if status:
            status = int(status)
            needs = needs.filter_by(status=status)

        if is_reported:
            is_reported = bool(int(is_reported))
            needs = needs.filter_by(isReported=is_reported)

        if ngo_id and sw_role in [
            SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
        ]:
            ngo_id = int(ngo_id)
            needs = needs \
                .join(Child) \
                .join(SocialWorker) \
                .filter(SocialWorker.id_ngo == ngo_id)

        needs = filter_by_privilege(needs, get=True)

        result = OrderedDict(
            totalCount=needs.count(),
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

            result['needs'].append(res)

        return result


class GetNeedById(Resource):

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN, USER)  # TODO: priv
    @json
    @swag_from('./docs/need/id.yml')
    def get(self, need_id):
        need_query = session.query(Need) \
            .filter_by(isDeleted=False) \
            .filter_by(id=need_id)

        need = filter_by_privilege(need_query, get=True).one_or_none()

        if need is None:
            raise HTTP_NOT_FOUND()

        need_dict = obj_to_dict(need)

        need_dict['participants'] = [
            obj_to_dict(p) for p in need.current_participants
        ]
        return need_dict


class UpdateNeedById(Resource):

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/need/update.yml')
    def patch(self, need_id):
        sw_role = get_user_role()

        need_query = session.query(Need) \
            .filter_by(id=need_id) \
            .filter_by(isDeleted=False)

        need = filter_by_privilege(need_query).one_or_none()

        if need is None:
            raise HTTP_NOT_FOUND()

        child = need.child
        temp_need_path = os.path.join(
            configs.UPLOAD_FOLDER, str(child.id) + '-child'
        )
        temp_need_path = os.path.join(temp_need_path, 'needs')
        temp_need_path = os.path.join(
            temp_need_path, str(need.id) + '-need'
        )

        if not os.path.isdir(temp_need_path):
            os.makedirs(temp_need_path, exist_ok=True)

        if 'receipts' in request.files.keys():
            file2 = request.files['receipts']
            if file2.filename == '':
                return {'message': 'ERROR OCCURRED --> EMPTY FILE!'}, 400

            if file2 and allowed_receipt(file2.filename):
                filename = secure_filename(uuid4().hex + '-' + file2.filename)
                if not os.path.isdir(temp_need_path):
                    os.makedirs(temp_need_path, exist_ok=True)

                receipt_path = os.path.join(
                    temp_need_path, str(need.id) + '-receipt_' + filename
                )

                file2.save(receipt_path)
                receipt_url = '/' + receipt_path
                if need.receipts is None:
                    need.receipts = receipt_url
                else:
                    need.receipts += f',{receipt_url}'

        # FIXME: receipts are allowed
        if need.isConfirmed and sw_role not in (ADMIN, SUPER_ADMIN):
            safe_commit(session)
            need_dict = obj_to_dict(need)
            return need_dict

        if 'cost' in request.form.keys():
            new_cost = int(request.form['cost'].replace(',', ''))

            if (
                ((sw_role in [SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR] and need.isConfirmed) or need.isDone) 
                and 
                new_cost != need._cost
            ):
                return {'message': 'Can not change cost when need is done'}, 400

            need.cost = new_cost

        if 'imageUrl' in request.files.keys():
            file = request.files['imageUrl']

            if file.filename == '':
                return {'message': 'ERROR OCCURRED --> EMPTY FILE!'}, 400

            if file and allowed_image(file.filename):
                filename = secure_filename(file.filename)
                filename = str(need.id) + '.' + filename.split('.')[-1]
                for obj in os.listdir(temp_need_path):
                    check = str(need.id) + '-image'

                    if obj.split('_')[0] == check:
                        os.remove(os.path.join(temp_need_path, obj))

                need.imageUrl = os.path.join(
                    temp_need_path, str(need.id) + '-image_' + uuid4().hex + filename
                )
                file.save(need.imageUrl)
                need.imageUrl = '/' + need.imageUrl

        if 'category' in request.form.keys():
            need.category = int(request.form['category'])

        if 'type' in request.form.keys():
            need.type = int(request.form['type'])

        if 'isUrgent' in request.form.keys():
            need.isUrgent = (
                True if request.form['isUrgent'] == 'true' else False
            )

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

        if dkc := request.form.get('dkc'):
            need.dkc = dkc

        if request.form.get('expected_delivery_date'):
            if not (2 <= need.status <= 3):
                raise Exception(
                    'Expected delivery date can not changed in this status'
                )
            need.isReported = False
            need.expected_delivery_date = parse_datetime(
                request.form['expected_delivery_date']
            )
        
        prev_status = need.status

        if 'status' in request.form.keys():
            new_status = int(request.form['status'])

            purchase_cost = request.form.get('purchase_cost', None)
            if purchase_cost and sw_role in [
                SUPER_ADMIN, SAY_SUPERVISOR, ADMIN,
            ] and new_status == 3 and need.type == 1:

                purchase_cost = purchase_cost.replace(',', '')
                need.purchase_cost = purchase_cost
                if need.purchase_date is not None:
                    need.oncePurchased = True

            if new_status != 5 and new_status - prev_status == 1:
                if new_status == 4 and need.isReported != True:
                    return {'message': 'Need has not been reported to ngo yet'}, 400

                need.status = new_status

            elif new_status != prev_status:
                return {
                    'message':
                        f'Can not change status from '
                        f'{prev_status} to {new_status}',
                    }, 400

        if need.type == 0 and need.status == 3:
            bank_track_id = request.form.get('bank_track_id')
            
            if not bank_track_id and prev_status == 2:
                raise ValueError(f'bank_track_id is required')
            
            if bank_track_id:
                need.bank_track_id = bank_track_id

        safe_commit(session)
        return need


class DeleteNeedById(Resource):

    @json
    @commit
    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from('./docs/need/delete.yml')
    def patch(self, need_id):
        need = session.query(Need) \
            .filter_by(isDeleted=False) \
            .filter_by(id=need_id)
        
        need = filter_by_privilege(need).one_or_none()

        if not need:
            return {'message': 'need not found'}, 404

        if get_user_role() in (SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR) \
                and need.isConfirmed:
            return {'message': 'permision denied'}, 403

        if (need.type == 0 and need.status < 4) or (need.type == 1 and need.status < 5):
            need.status = 0
            need.purchase_cost = None
            need.refund_extra_credit(new_paid=0)

            for participant in need.participants:
                participant.isDeleted = True

            need.isDeleted = True
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

        if primary_need.isConfirmed:
            return {'message': 'need has already been confirmed!'}, 400

        child = primary_need.child

        primary_need.isConfirmed = True
        primary_need.confirmUser = social_worker_id
        primary_need.confirmDate = datetime.utcnow()

        new_child_need = ChildNeed(
            id_child=child.id,
            id_need=primary_need.id,
        )

        child.social_worker.needCount += 1
        child.social_worker.currentNeedCount += 1

        session.add(new_child_need)
        safe_commit(session)

        return {'message': 'need confirmed successfully!'}


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

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @swag_from('./docs/need/add.yml')
    def post(self):
        child_id = int(request.form['child_id'])
        child = session.query(Child) \
            .filter_by(id=child_id) \
            .filter_by(isDeleted=False) \
            .filter_by(isMigrated=False) \
            .filter_by(isConfirmed=True) \
            .one_or_none()

        sw_id = int(request.form.get('sw_id', get_user_id()))
        sw_role = get_user_role()

        allowed_sw_ids = []
        if sw_role in [NGO_SUPERVISOR]:
            allowed_sw_ids_tuple = session.query(SocialWorker.id) \
                .filter_by(isDeleted=False) \
                .filter_by(id_ngo=get_sw_ngo_id()) \
                .distinct() \
                .all()

            allowed_sw_ids = [item[0] for item in allowed_sw_ids_tuple]

        # May throw
        self.check_privilege(sw_id, allowed_sw_ids)

        if not child.isConfirmed:
            return {'message': 'error: child is not confirmed yet!'}, 400

        image_path, receipt_path = 'wrong path', None

        image_url = image_path
        receipts = receipt_path

        category = int(request.form['category'])
        cost = request.form['cost'].replace(',', '')

        name_translations = ujson.loads(
            request.form['name_translations']
        )
        description_translations = ujson.loads(
            request.form['description_translations'],
        )

        is_urgent = True if request.form['isUrgent'] == 'true' else False
        need_type = request.form['type']

        details = request.form.get('details', '')
        last_update = datetime.utcnow()
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
            name_translations=name_translations,
            description_translations=description_translations,
            imageUrl=image_url,
            category=category,
            cost=cost,
            isUrgent=is_urgent,
            affiliateLinkUrl=affiliate_link_url,
            link=link,
            receipts=receipts,
            type=need_type,
            child=child,
            doing_duration=doing_duration,
            details=details,
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
        temp_need_path = os.path.join(needs_path, need_dir)

        if 'imageUrl' in request.files:
            file = request.files['imageUrl']
            if not allowed_image(file.filename):
                return {'message': 'Invalid image'}, 400

            filename = str(new_need.id) + '.' + file.filename.split('.')[-1]

            if not os.path.isdir(temp_need_path):
                os.makedirs(temp_need_path, exist_ok=True)

            image_path = os.path.join(
                temp_need_path, str(new_need.id) + '-image_' + filename
            )

            file.save(image_path)
            new_need.imageUrl = '/' + image_path

        # Depreceted
        if "receipts" in request.files.keys():
            file2 = request.files["receipts"]
            if file2.filename == "":
                resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY FILE!"}), 500)
                session.close()
                return resp


            if not allowed_receipt(file2.filename):
                resp = make_response(jsonify({"message": f"Only {ALLOWED_RECEIPT_EXTENSIONS} allowed"}), 400)
                session.close()
                return resp

            filename = secure_filename(file2.filename)

            temp_need_path = os.path.join(
                temp_need_path, str(new_need.id) + "-need"
            )

            if not os.path.isdir(temp_need_path):
                os.makedirs(temp_need_path, exist_ok=True)

            receipt_path = os.path.join(
                temp_need_path, str(new_need.id) + "-receipt_" + filename
            )

            file2.save(receipt_path)
            new_need.receipts = '/' + receipt_path

            safe_commit(session)

            if new_need.link:
                update_need.delay(new_need.id)

            resp = make_response(jsonify(obj_to_dict(new_need)), 200)

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

        base_query = (session.query(Receipt) \
            .join(NeedReceipt, NeedReceipt.receipt_id == Receipt.id)
            .join(Need, NeedReceipt.need_id == Need.id)
            .join(Child, Child.id == Need.child_id)
            .join(SocialWorker, SocialWorker.id == Child.id_social_worker)
            .filter(
                Need.isDeleted == False,
                Receipt.deleted.is_(None),
                NeedReceipt.deleted.is_(None),
                Need.id == id,
                or_(
                    True if user_role in [SUPER_ADMIN, ADMIN, SAY_SUPERVISOR] else False,
                    Receipt.is_public == True,
                    Receipt.owner_id == user_id if not user_role in [SUPER_ADMIN, ADMIN, SAY_SUPERVISOR] else False,
                    SocialWorker.id_ngo == ngo_id if user_role in [NGO_SUPERVISOR] else False,
                ),
            )
        )

        res = []
        for r in base_query:
            res.append(ReceiptSchema.from_orm(r))

        return res
        

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from('./docs/need/new_receipt.yml')
    def post(self, id):
        sw_id = get_user_id()

        try:
            data = NewReceiptSchema(**request.form.to_dict(), **request.files, owner_id=sw_id)
        except ValueError as e:
            return e.json(), 400


        need = filter_by_privilege(
            session.query(Need).filter(
                Need.id == id,
                Need.isDeleted == False,
            )
        ).one_or_none()


        if need is None:
            return HTTP_NOT_FOUND()
        
        receipt = session.query(Receipt).filter(
            Receipt.code == data.code,
            Receipt.deleted == None,
        ).one_or_none()

        if receipt is not None:
            return {'message': 'Code already exists'}, 400

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
        return ReceiptSchema.from_orm(receipt)


class NeedReceiptAPI(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from('./docs/need/delete_receipt.yml')
    def delete(self, id, receiptId):
        receipt_id = receiptId
        need_receipt = session.query(NeedReceipt).filter(
            NeedReceipt.need_id == id,
            NeedReceipt.receipt_id == receipt_id,
            NeedReceipt.deleted.is_(None),
        ).one_or_none()

        if need_receipt is None:
            return HTTP_NOT_FOUND()

        need_receipt.deleted = datetime.utcnow()
        safe_commit(session)
        return ReceiptSchema.from_orm(need_receipt.receipt)
        
        

"""
API URLs
"""

api.add_resource(GetNeedById, '/api/v2/need/needId=<need_id>')
api.add_resource(GetAllNeeds, '/api/v2/need/all/confirm=<confirm>')
api.add_resource(UpdateNeedById, '/api/v2/need/update/needId=<need_id>')
api.add_resource(DeleteNeedById, '/api/v2/need/delete/needId=<need_id>')
api.add_resource(
    ConfirmNeed,
    '/api/v2/need/confirm/needId=<need_id>',
)
api.add_resource(AddNeed, "/api/v2/need/")
api.add_resource(
    NeedReceipts,
    "/api/v2/needs/<int:id>/receipts",
)
api.add_resource(
    NeedReceiptAPI,
    "/api/v2/needs/<int:id>/receipts/<int:receiptId>",
)
