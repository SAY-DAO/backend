"""empty message

Revision ID: afbcf9baae46
Revises: 77587813ac82
Create Date: 2019-11-09 19:10:25.674729

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afbcf9baae46'
down_revision = '77587813ac82'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE "user" ADD UNIQUE ("emailAddress");
    ''')


def downgrade():
    pass
