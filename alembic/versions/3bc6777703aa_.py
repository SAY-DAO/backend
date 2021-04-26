"""empty message

Revision ID: 3bc6777703aa
Revises: 5c91461b0019
Create Date: 2019-11-10 21:11:37.375287

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '3bc6777703aa'
down_revision = '5c91461b0019'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE activity
            ADD COLUMN diff JSONB;
    ''')
    op.execute('''
        ALTER TABLE activity
            ADD COLUMN model TEXT;
    ''')
    op.execute('''
        ALTER TABLE activity
            ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
    ''')

def downgrade():
    op.execute('''
        ALTER TABLE activity
            DROP COLUMN diff ;
    ''')
    op.execute('''
        ALTER TABLE activity
            DROP COLUMN model ;
    ''')
    op.execute('''
        ALTER TABLE activity
            DROP COLUMN created_at;
    ''')
