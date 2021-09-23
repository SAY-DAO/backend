"""empty message

Revision ID: fe214bd981c5
Revises: 654453a18f24
Create Date: 2021-04-27 18:16:18.084676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe214bd981c5'
down_revision = '654453a18f24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invitations', 'see_count')
    op.alter_column('need', 'purchase_cost', existing_type=sa.INTEGER(), nullable=True)

    op.execute(
        '''
        UPDATE need set purchase_cost = null where status < 3;
    '''
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('need', 'purchase_cost', existing_type=sa.INTEGER(), nullable=False)
    op.add_column(
        'invitations',
        sa.Column('see_count', sa.INTEGER(), autoincrement=False, nullable=False),
    )
    # ### end Alembic commands ###
