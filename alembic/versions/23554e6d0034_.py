"""empty message

Revision ID: 23554e6d0034
Revises: 389f9919c78d
Create Date: 2022-11-19 18:31:18.927450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23554e6d0034'
down_revision = 'fa7d127f259b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('need_status_updates',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('need_id', sa.Integer(), nullable=True),
    sa.Column('sw_id', sa.Integer(), nullable=True),
    sa.Column('old_status', sa.Integer(), nullable=True),
    sa.Column('new_status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['need_id'], ['need.id'], name=op.f('need_status_updates_need_id_need_fkey')),
    sa.ForeignKeyConstraint(['sw_id'], ['social_worker.id'], name=op.f('need_status_updates_sw_id_social_worker_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('need_status_updates_pkey'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
