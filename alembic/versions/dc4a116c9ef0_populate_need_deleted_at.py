"""Populate need.deleted_at

Revision ID: dc4a116c9ef0
Revises: 991de8e47ed0
Create Date: 2021-09-08 15:58:33.564274

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'dc4a116c9ef0'
down_revision = '991de8e47ed0'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        'UPDATE need SET deleted_at = updated WHERE "isDeleted" = true;'
    )


def downgrade():
    pass
