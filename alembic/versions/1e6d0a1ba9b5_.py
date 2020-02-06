"""empty message

Revision ID: 1e6d0a1ba9b5
Revises: d541c4d2fcd0
Create Date: 2020-02-06 21:45:01.129125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e6d0a1ba9b5'
down_revision = 'd541c4d2fcd0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'need',
        sa.Column('purchase_cost', sa.Integer(), nullable=True)
    )
    op.execute('''
        UPDATE need set purchase_cost = _cost;
    ''')
    op.execute('''
        ALTER TABLE need ALTER COLUMN purchase_cost SET NOT NULL;
    ''')

    op.drop_column('need', 'cost_variance')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('need', sa.Column('cost_variance', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.drop_column('need', 'purchase_cost')
    # ### end Alembic commands ###
