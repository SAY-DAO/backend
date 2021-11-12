"""empty message

Revision ID: 5efe79cc2116
Revises: b4d388c3cfca
Create Date: 2021-11-12 15:39:20.487702

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '5efe79cc2116'
down_revision = 'b4d388c3cfca'
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
        Need.isConfirmed is True,
        Need.isDeleted is False,
    )
    print('These needs are done but stuck in status 0 and 1:')
    for need in needs:
        print(f'Need: id: {need.id} cost: {need.cost} paid: {need.paid}')


def downgrade():
    pass
