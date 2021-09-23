"""empty message

Revision ID: 9b05b9b45ab0
Revises: 22774c633395
Create Date: 2020-11-13 01:47:39.272343

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = '9b05b9b45ab0'
down_revision = '22774c633395'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'nakama_owners',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('address', sa.Unicode(length=64), nullable=False),
        sa.PrimaryKeyConstraint('address', name=op.f('nakama_owners_pkey')),
    )
    op.create_table(
        'nakama_txs',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('id', sa.Unicode(length=120), nullable=False),
        sa.Column('sender_address', sa.Unicode(length=64), nullable=True),
        sa.Column('need_id', sa.Integer(), nullable=True),
        sa.Column('value', sa.BigInteger(), nullable=True),
        sa.Column('is_confirmed', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ['need_id'], ['need.id'], name=op.f('nakama_txs_need_id_need_fkey')
        ),
        sa.ForeignKeyConstraint(
            ['sender_address'],
            ['nakama_owners.address'],
            name=op.f('nakama_txs_sender_address_nakama_owners_fkey'),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('nakama_txs_pkey')),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('nakama_txs')
    op.drop_table('nakama_owners')
    # ### end Alembic commands ###
