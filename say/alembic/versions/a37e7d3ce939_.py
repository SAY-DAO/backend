"""empty message

Revision ID: a37e7d3ce939
Revises: df912c582af4
Create Date: 2019-12-02 18:47:27.232170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a37e7d3ce939'
down_revision = 'df912c582af4'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('''
        ALTER TABLE need
            RENAME COLUMN "delivereDate" TO delivery_date;
    ''')


def downgrade():
    op.execute('''
        ALTER TABLE need
            RENAME COLUMN delivery_date TO "delivereDate";
    ''')

