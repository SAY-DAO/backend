"""empty message

Revision ID: 8a0bca2890cc
Revises: fd994736750c
Create Date: 2020-10-03 16:06:56.790501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a0bca2890cc'
down_revision = 'fd994736750c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('child', 'spent_credit')
    op.drop_column('child', 'done_needs_count')
    op.create_unique_constraint(op.f('family_id_child_key'), 'family', ['id_child'])
    op.drop_column('need', 'paid')
    op.drop_column('need', 'donated')
    op.drop_column('need_family', 'paid')
    op.drop_column('user', 'spent')
    op.drop_column('user', 'done_needs_count')
    op.drop_column('user', 'credit')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('credit', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('done_needs_count', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('spent', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.add_column('need_family', sa.Column('paid', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.add_column('need', sa.Column('donated', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.add_column('need', sa.Column('paid', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.drop_constraint(op.f('family_id_child_key'), 'family', type_='unique')
    op.add_column('child', sa.Column('done_needs_count', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    op.add_column('child', sa.Column('spent_credit', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    # ### end Alembic commands ###