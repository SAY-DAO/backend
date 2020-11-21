# ADD need to receipt
# Update receipt
# Delete receipt

from flask_restful import Resource
from say.models import Receipt, session
from say.models.receipt import NeedReceipt
from say.orm import safe_commit
from say.schema import NewReceiptSchema, ReceiptSchema

from . import *


class ReceiptAPI(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from('./docs/receipt/delete_receipt.yml')
    def delete(self, id):
        receipt = session.query(Receipt).get(id)

        if receipt is None:
            return HTTP_NOT_FOUND()

        if receipt.deleted:
            return {'message': 'Already deleted'}

        now = datetime.utcnow()
        receipt.deleted = now

        session.query(NeedReceipt) \
            .filter(
                NeedReceipt.receipt_id == id,
                NeedReceipt.deleted.is_(None),
            ).update({NeedReceipt.deleted: now})
 
        safe_commit(session)
        return ReceiptSchema.from_orm(receipt)

api.add_resource(
    ReceiptAPI,
    "/api/v2/receipts/<int:id>",
)
