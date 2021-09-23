"""empty message

Revision ID: 67a28a3f9f9f
Revises: fe214bd981c5
Create Date: 2021-07-06 16:49:33.642799

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '67a28a3f9f9f'
down_revision = 'fe214bd981c5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'need', sa.Column('informations', sa.String(length=1024), nullable=True)
    )
    op.execute(
        'UPDATE need set informations = details, details = null where need.type = 1;'
    )
    # op.execute('UPDATE need set details = null where need.type = 1;')
    # ### end Alembic commands ###


def downgrade():
    op.execute('UPDATE need set details = informations where need.type = 1;')
    op.drop_column('need', 'informations')
    # ### end Alembic commands ###
