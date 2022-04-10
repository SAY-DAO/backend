"""empty message

Revision ID: 0dc7eeb9c798
Revises: d694326b71aa
Create Date: 2022-03-28 18:06:16.246973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dc7eeb9c798'
down_revision = 'd694326b71aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('need', sa.Column('created_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('need_created_by_id_social_worker_fkey'), 'need', 'social_worker', ['created_by_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('need_created_by_id_social_worker_fkey'), 'need', type_='foreignkey')
    op.drop_column('need', 'created_by_id')
    # ### end Alembic commands ###