"""empty message

Revision ID: 7648ed29f9be
Revises: d594919df769
Create Date: 2019-12-29 12:44:35.512769

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '7648ed29f9be'
down_revision = 'd594919df769'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE need
            ALTER COLUMN delivery_date TYPE TIMESTAMP;
    ''')
    op.execute('''
        ALTER TABLE need
            RENAME COLUMN delivery_date TO ngo_delivery_date;
    ''')
    op.execute('''
        ALTER TABLE need
            ADD COLUMN purchase_date TIMESTAMP;
    ''')
    op.execute('''
        ALTER TABLE need
            ADD COLUMN child_delivery_date TIMESTAMP;
    ''')
    op.execute('''
        ALTER TABLE need
            ADD COLUMN expected_delivery_date TIMESTAMP;
    ''')


def downgrade():
    op.execute('''
        ALTER TABLE need
            RENAME COLUMN ngo_delivery_date TO delivery_date;
    ''')
    op.execute('''
        ALTER TABLE need
            ALTER COLUMN delivery_date TYPE DATE;
    ''')
    op.execute('''
        ALTER TABLE need
            DROP COLUMN purchase_date;
    ''')
    op.execute('''
        ALTER TABLE need
            DROP COLUMN child_delivery_date;
    ''')
    op.execute('''
        ALTER TABLE need
            DROP COLUMN expected_delivery_date;
    ''')

