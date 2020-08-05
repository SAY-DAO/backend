"""empty message

Revision ID: c0c97e8069b3
Revises: d162c5703e01
Create Date: 2019-12-01 16:00:53.517476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0c97e8069b3'
down_revision = 'd162c5703e01'
branch_labels = None
depends_on = None


def upgrade():
     op.execute('''
        ALTER TABLE need
            ADD COLUMN "isReported" BOOLEAN;
    ''')
     op.execute('''
        ALTER TABLE need
            ADD COLUMN "delivereDate" DATE;
    ''')

def downgrade():
     op.execute('''
        ALTER TABLE need
            DROP COLUMN "isReported";
    ''')
     op.execute('''
        ALTER TABLE need
            DROP COLUMN "delivereDate";
    ''')
