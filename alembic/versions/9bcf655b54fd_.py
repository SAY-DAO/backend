"""empty message

Revision ID: 9bcf655b54fd
Revises: a37e7d3ce939
Create Date: 2019-12-04 13:05:53.680959

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '9bcf655b54fd'
down_revision = 'a37e7d3ce939'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE need
            ADD COLUMN img TEXT;
    ''')
    op.execute('''
        ALTER TABLE need
            ADD COLUMN title TEXT;
    ''')

def downgrade():
    pass
