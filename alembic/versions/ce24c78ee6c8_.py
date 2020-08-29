"""empty message

Revision ID: ce24c78ee6c8
Revises: 3868cd9f04f2
Create Date: 2020-08-29 16:31:24.821526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce24c78ee6c8'
down_revision = '3868cd9f04f2'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE "user" SET "avatarUrl" = \'/public/resources/img/default-avatar.png\' WHERE "avatarUrl" is NULL')
    op.alter_column('user', 'avatarUrl',
               existing_type=sa.VARCHAR(),
               nullable=False
    )

def downgrade():
    pass
