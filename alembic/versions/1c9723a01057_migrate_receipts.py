"""migrate-receipts

Revision ID: 1c9723a01057
Revises: e54fada30e55
Create Date: 2021-08-23 13:18:43.390434

"""
from uuid import uuid4

from alembic import op


# revision identifiers, used by Alembic.
revision = '1c9723a01057'
down_revision = 'e54fada30e55'
branch_labels = None
depends_on = None


def upgrade():
    from say.models import Need
    from say.models import NeedReceipt
    from say.models import Receipt
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())

    op.execute(
        'alter table receipt alter column attachment type character varying(256);'
    )
    op.execute('alter table receipt alter column code type character varying(128);')

    needs = session.query(Need)
    for need in needs:
        if need.receipts is None:
            continue

        for old_receipt in need.receipts.split(','):
            receipt = NeedReceipt(
                receipt=Receipt(
                    owner_id=need.child.id_social_worker,
                    code=f'legacy-{need.id}-{uuid4().hex}',
                    attachment=old_receipt,
                    is_public=False,
                ),
                need=need,
                sw_id=need.child.id_social_worker,
            )
            session.add(receipt)

    session.commit()


def downgrade():
    pass
