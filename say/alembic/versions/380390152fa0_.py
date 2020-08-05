"""empty message

Revision ID: 380390152fa0
Revises: 91fedb2a59c4
Create Date: 2019-10-14 17:23:12.769656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '380390152fa0'
down_revision = '91fedb2a59c4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE ngo
            ALTER COLUMN "registerDate" TYPE TIMESTAMP;
    ''')
    op.execute('''
        ALTER TABLE ngo
            ALTER COLUMN "lastUpdateDate" TYPE TIMESTAMP;
    ''')


def downgrade():
    pass
