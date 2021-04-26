"""empty message

Revision ID: 091009b644e8
Revises: 9c60e2651393
Create Date: 2019-12-31 18:01:32.136926

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '091009b644e8'
down_revision = '9c60e2651393'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('need', sa.Column('descriptionSummary_fa', sa.Text(), nullable=True))
    op.add_column('need', sa.Column('description_fa', sa.Text(), nullable=True))
    op.add_column('need', sa.Column('name_fa', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('need', 'name_fa')
    op.drop_column('need', 'description_fa')
    op.drop_column('need', 'descriptionSummary_fa')
    # ### end Alembic commands ###
