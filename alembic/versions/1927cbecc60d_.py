"""empty message

Revision ID: 1927cbecc60d
Revises: 5f88cc67b8d4
Create Date: 2020-02-18 18:07:13.318806

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '1927cbecc60d'
down_revision = '5f88cc67b8d4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE need ALTER COLUMN "doneAt" type timestamp without time zone;
    ''')

    op.execute('''
        ALTER TABLE need ALTER COLUMN "confirmDate" type timestamp without time zone;
    ''')


def downgrade():
    pass
