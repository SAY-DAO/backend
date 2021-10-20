"""This migration fixes diffence between cost and paid of some needs due to a bug in say extra payment,
patch commit hash: 114312ad8e060274ec481353ea25f960e2afe50d

Revision ID: 92e7bd6272b0
Revises: 0bae2c4e2f34
Create Date: 2021-10-20 19:39:01.082843

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '92e7bd6272b0'
down_revision = '0bae2c4e2f34'
branch_labels = None
depends_on = None


def upgrade():
    from say.models import Need
    from say.models import Payment
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())

    bad_needs = session.query(Need).filter(
        Need.status >= 3,
        Need.paid != Need.cost,
    )
    bad_needs_id = [n.id for n in bad_needs]
    say_payments = session.query(Payment).filter(
        Payment.id_need.in_(bad_needs_id),
        Payment.desc == 'SAY payment',
    )

    total_diff = 0
    for p in say_payments:
        diff = p.need.cost - p.need.paid
        total_diff += diff
        new_amount = p.need_amount + diff
        print(f'Updating payment {p.id}: amount from {p.need_amount} to {new_amount}')
        p.need_amount = new_amount

    print(f'### TOTAL DIFF: {total_diff}')
    session.commit()
    # raise ValueError()


def downgrade():
    pass
