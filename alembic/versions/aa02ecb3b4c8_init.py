"""init

Revision ID: aa02ecb3b4c8
Revises:
Create Date: 2019-10-05 21:41:46.731553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa02ecb3b4c8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'revoked_tokens',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('jti', sa.Unicode(200)),
    )
    pass


def downgrade():
    pass
