"""Delete unconfirmed needs of gone children

Revision ID: 991de8e47ed0
Revises: 6b49c131765d
Create Date: 2021-09-08 15:38:24.797831

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '991de8e47ed0'
down_revision = '6b49c131765d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''UPDATE need
        SET "isDeleted" = true, deleted_at = NOW()::timestamp, unconfirmed_at = need.updated, updated = NOW()::timestamp
        FROM child
        WHERE child.id = need.child_id and child.existence_status != 1 and need."isDeleted" = false and  need."isConfirmed" is false;
        '''
    )


def downgrade():
    pass
