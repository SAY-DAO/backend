# ADD need to receipt

from flask import abort
from flask_restful import Resource
from sqlalchemy import or_

from say.models import Need, Receipt, session
from say.models.child_model import Child
from say.models.receipt import NeedReceipt
from say.models.social_worker_model import SocialWorker
from say.orm import safe_commit
from say.schema import ReceiptSchema, UpdateReceiptSchema

from . import *


def filter_by_privilege(query, get=False):  # TODO: priv
    user_role = get_user_role()
    user_id = get_user_id()
    ngo_id = get_sw_ngo_id()

    if user_role in [SOCIAL_WORKER, COORDINATOR]:
        if get:
            query = query.join(NeedReceipt).join(Need).join(Child).filter(
                or_(
                    Child.id_social_worker == user_id,
                    Child.id == DEFAULT_CHILD_ID,
                ),
                Child.isDeleted == False,
            )
        else:
            query = query.join(NeedReceipt).join(Need).join(Child).filter(
                Child.id_social_worker == user_id,
                Child.isDeleted == False,
            )

    elif user_role in [NGO_SUPERVISOR]:
        if get:
            query = query \
                .join(NeedReceipt) \
                .join(Need) \
                .join(Child) \
                .join(SocialWorker) \
                .filter(or_(
                    SocialWorker.id_ngo == ngo_id,
                    Child.id == DEFAULT_CHILD_ID,
                ))
        else:
            query = query \
                .join(NeedReceipt) \
                .join(Need) \
                .join(Child) \
                .join(SocialWorker) \
                .filter(
                    SocialWorker.id_ngo == ngo_id,
                )

    return query
    

class ReceiptAPI(Resource):
    def _get_or_404(self, id):
        receipt = filter_by_privilege(session.query(Receipt).filter(
            Receipt.id == id,
            Receipt.deleted.is_(None),
        )).one_or_none()

        if receipt is None:
            abort(404)
        
        return receipt

    def _check_for_update(self, receipt):
        role = get_user_role()

        if role in [SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR] \
                and receipt.is_public:

            abort(403)

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from('./docs/receipt/delete.yml')
    def delete(self, id):
        receipt = self._get_or_404(id)

        self._check_for_update(receipt)

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
        receipt = self._get_or_404(id)
        self._check_for_update(receipt)

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


api.add_resource(
    ReceiptAPI,
    "/api/v2/receipts/<int:id>",
)
