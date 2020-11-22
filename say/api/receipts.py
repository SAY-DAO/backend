from flask import abort
from flask_restful import Resource

from say.models import Need, Receipt, session
from say.models.receipt import NeedReceipt
from say.orm import safe_commit
from say.schema import ReceiptSchema, UpdateReceiptSchema

from . import *


class ReceiptAPI(Resource):
    def _get_or_404(self, id, for_update=False):
        role = get_user_role()
        user_id = get_user_id()
        ngo_id = get_sw_ngo_id()
        
        receipt = Receipt._query(session, role, user_id, ngo_id, for_update).filter(
            Receipt.id == id,
        ).one_or_none()

        if receipt is None:
            abort(404)
        
        return receipt

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



api.add_resource(
    ReceiptAPI,
    '/api/v2/receipts/<int:id>',
)
api.add_resource(
    AttachReceiptAPI,
    '/api/v2/receipts/<int:id>/needs/<int:need_id>',
)
