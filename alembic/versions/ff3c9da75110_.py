"""empty message

Revision ID: ff3c9da75110
Revises: 5637c5fe8dca
Create Date: 2020-01-20 18:28:41.066392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff3c9da75110'
down_revision = '5637c5fe8dca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('need', 'isDone')
    op.add_column('need_family', sa.Column(
            'paid',
            sa.Integer(),
            nullable=False,
            server_default='0',
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('need_family', 'paid')
    op.add_column('need', sa.Column('isDone', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
