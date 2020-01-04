"""empty message

Revision ID: 9971e0f64c65
Revises: 8713162b738f
Create Date: 2019-12-31 19:15:12.430928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9971e0f64c65'
down_revision = '8713162b738f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        UPDATE need set expected_delivery_date = ngo_delivery_date;
    ''')

    op.execute('''
        UPDATE need set child_delivery_date = ngo_delivery_date;
    ''')


def downgrade():
    pass
