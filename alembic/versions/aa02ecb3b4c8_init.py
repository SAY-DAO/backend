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
        'verify',
        sa.Column('id', sa.Integer, primary_key=True, unique=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('code', sa.Integer, nullable=False),
        sa.Column('expire_at', sa.DateTime, nullable=False),
    )

    op.create_table(
        'revoked_tokens',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('jti', sa.Unicode(200)),
    )
    pass


def downgrade():
    op.drop_table('verify')
    op.drop_table('revoked_tokens')
