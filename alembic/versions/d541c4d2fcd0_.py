"""empty message

Revision ID: d541c4d2fcd0
Revises: 7b988b91284f
Create Date: 2020-02-05 21:33:40.903500

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd541c4d2fcd0'
down_revision = '7b988b91284f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('need', sa.Column('cost_variance', sa.Integer(), nullable=False, server_default='0'))
    op.drop_column('need', 'purchase_cost')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('need', sa.Column('purchase_cost', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('need', 'cost_variance')
    # ### end Alembic commands ###