"""empty message

Revision ID: 1c89b563da22
Revises: bb128d1d1376
Create Date: 2021-11-12 17:12:09.485354

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '1c89b563da22'
down_revision = 'bb128d1d1376'
branch_labels = None
depends_on = None


def upgrade():
    from say.models import Need
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())

    needs = session.query(Need).filter(
        Need.status.in_([0, 1]),
        Need.paid >= Need.cost,
        Need.paid > 0,
    )
    print('These needs are done but stuck in status 0 and 1:')
    for need in needs:
        print(f'Need: id: {need.id} cost: {need.cost} paid: {need.paid}')
        need.done()

    session.commit()


def downgrade():
    pass
