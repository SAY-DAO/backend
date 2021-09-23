"""empty message

Revision ID: 3a1a0f992985
Revises: 33e4624b36d6
Create Date: 2020-01-11 20:03:47.851575

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = '3a1a0f992985'
down_revision = '33e4624b36d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'activity', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'activity', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'child', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'child', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'child_need', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'child_need', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'family', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'family', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'need', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'need', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'need_family', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'need_family', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'ngo', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'ngo', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'payment', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'payment', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'social_worker', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'social_worker', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'social_worker_type',
        'created',
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.alter_column(
        'social_worker_type',
        'updated',
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.alter_column(
        'user', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'user', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'user_family', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'user_family', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'verify', 'created', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        'verify', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'verify', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'verify', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'user_family', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'user_family', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'user', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'user', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'social_worker_type',
        'updated',
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.alter_column(
        'social_worker_type',
        'created',
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.alter_column(
        'social_worker', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'social_worker', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'payment', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'payment', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'ngo', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'ngo', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'need_family', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'need_family', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'need', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'need', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'family', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'family', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'child_need', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'child_need', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'child', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'child', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'activity', 'updated', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        'activity', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    # ### end Alembic commands ###
