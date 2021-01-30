from flask import abort
from flask_restful import Resource
from flask_jwt_extended.exceptions import NoAuthorizationError
from sqlalchemy import or_, func

from say.models import Need, Receipt, session, Child, SocialWorker
from say.models.receipt import NeedReceipt
from say.orm import safe_commit
from say.schema import ReceiptSchema, UpdateReceiptSchema
from say.pagination import paginate

from . import *


class ReceiptAPI(Resource):
    def _get_or_404(self, id, for_update=False):
        try:
            user_role = get_user_role()
            user_id = get_user_id()
            ngo_id = get_sw_ngo_id()
        except NoAuthorizationError:
            user_role = None
            user_id = None
            ngo_id = None
        
        receipt = Receipt._query(session, user_role, user_id, ngo_id, for_update).filter(
            Receipt.id == id,
        ).one_or_none()

        if receipt is None:
            abort(404)
        
        return receipt
    
    @json
    @swag_from('./docs/receipt/get.yml')
    def get(self, id):
        receipt = self._get_or_404(id, for_update=False)
        return ReceiptSchema.from_orm(receipt)
        
    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from('./docs/receipt/delete.yml')
    def delete(self, id):
        receipt = self._get_or_404(id, for_update=True)

        now = datetime.utcnow()
        receipt.deleted = now

        session.query(NeedReceipt) \
            .filter(
                NeedReceipt.receipt_id == id,
                NeedReceipt.deleted.is_(None),
            ).update({NeedReceipt.deleted: now})
 
        safe_commit(session)
        return ReceiptSchema.from_orm(receipt)


    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from('./docs/receipt/update.yml')
    def patch(self, id):
        receipt = self._get_or_404(id, for_update=True)

        try:
            data = UpdateReceiptSchema(
                **request.form.to_dict(), 
                **request.files,
            )
        except ValueError as e:
            return e.json(), 400
        
        receipt.update(**data.dict(skip_defaults=True))
        safe_commit(session)

        if data.attachment:
            data.attachment.save(data.attachment.filepath)

        return ReceiptSchema.from_orm(receipt)


class AttachReceiptAPI(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from('./docs/receipt/attach.yml')
    def post(self, id, need_id):
        role = get_user_role()
        user_id = get_user_id()

        exists = session.query(NeedReceipt).filter(
            NeedReceipt.need_id == need_id,
            NeedReceipt.receipt_id == id,
            NeedReceipt.deleted.is_(None),
        ).one_or_none()

        if exists:
            return {'message': 'Already attached'}, 400

        receipt_id = Receipt._query(session, role, user_id, fields=[Receipt.id]) \
            .filter(Receipt.id == id) \
            .one_or_none()
        
        if not receipt_id:
            abort(404)

        need_id = session.query(Need.id).filter(
            Need.id == need_id,
            Need.isDeleted == False,
            Need.isConfirmed == True,
        ).one_or_none()

        if not need_id:
            abort(404)
        
        need_receipt = NeedReceipt(need_id=need_id, receipt_id=receipt_id, sw_id=user_id)
        session.add(need_receipt)
        safe_commit(session)
        return need_receipt


class ListReceiptsAPI(Resource):

    @paginate
    @json
    @swag_from('./docs/receipt/list.yml')
    def get(self):
        search = request.args.get('search')

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
                or_(
                    True if user_role in [SUPER_ADMIN, ADMIN, SAY_SUPERVISOR] else False,
                    Receipt.is_public == True,
                    Receipt.owner_id == user_id if not user_role in [SUPER_ADMIN, ADMIN, SAY_SUPERVISOR] else False,
                    SocialWorker.id_ngo == ngo_id if user_role in [NGO_SUPERVISOR] else False,
                ),
            )
        )

        if search:
            base_query = base_query\
                .filter(func.similarity(Receipt.code, search) > 0.05) \
                .order_by(func.similarity(Receipt.code, search).desc())
        else:
            base_query = base_query \
                .order_by(Receipt.updated.desc(), Receipt.created.desc())
        
        res = []
        for r in base_query[request.skip:request.skip+request.take]:
            res.append(ReceiptSchema.from_orm(r))

        return res


api.add_resource(
    ReceiptAPI,
    '/api/v2/receipts/<int:id>',
)
api.add_resource(
    AttachReceiptAPI,
    '/api/v2/receipts/<int:id>/needs/<int:need_id>',
)
api.add_resource(
    ListReceiptsAPI,
    '/api/v2/receipts',
)