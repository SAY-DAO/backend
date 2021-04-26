"""empty message

Revision ID: a9e54919491a
Revises: afbcf9baae46
Create Date: 2019-11-10 15:15:11.311100

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'a9e54919491a'
down_revision = 'afbcf9baae46'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE payment
            ALTER COLUMN "date" TYPE TIMESTAMP WITH TIME ZONE;
    ''')
    op.execute('''
        ALTER TABLE payment
            ALTER COLUMN "createdAt" TYPE TIMESTAMP WITH TIME ZONE;
    ''')
    op.execute('''
        ALTER TABLE payment
            ALTER COLUMN "verfied_date" TYPE TIMESTAMP WITH TIME ZONE;
    ''')

def downgrade():
    pass
