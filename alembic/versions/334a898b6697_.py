"""empty message

Revision ID: 334a898b6697
Revises: 7edc4b2ac178
Create Date: 2020-02-01 17:46:02.278954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '334a898b6697'
down_revision = '7edc4b2ac178'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('update "user" set "emailAddress" = LOWER("emailAddress");')
    op.execute('update "user" set "userName" = LOWER("userName");')


def downgrade():
    pass
