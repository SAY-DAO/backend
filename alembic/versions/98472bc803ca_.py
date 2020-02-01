"""empty message

Revision ID: 98472bc803ca
Revises: 18e8746efd3f
Create Date: 2020-02-01 18:59:18.905240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98472bc803ca'
down_revision = '18e8746efd3f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('update "user" set "emailAddress" = LOWER("emailAddress");')
    op.execute('update "user" set "userName" = LOWER("userName");')


def downgrade():
    pass
