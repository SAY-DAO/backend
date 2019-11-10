"""empty message

Revision ID: 9ebc48eeec12
Revises: a9e54919491a
Create Date: 2019-11-10 15:18:38.135738

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ebc48eeec12'
down_revision = 'a9e54919491a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE need
            ADD COLUMN "doneAt" TIMESTAMP WITH TIME ZONE;
    ''')
    op.execute('''
        ALTER TABLE need
            ALTER COLUMN "createdAt" TYPE TIMESTAMP WITH TIME ZONE;
    ''')
    op.execute('''
        ALTER TABLE need
            ALTER COLUMN "confirmDate" TYPE TIMESTAMP WITH TIME ZONE;
    ''')
    op.execute('''
        ALTER TABLE need
            ALTER COLUMN "lastUpdate" TYPE TIMESTAMP WITH TIME ZONE;
    ''')

def downgrade():
    pass
