"""empty message

Revision ID: 893aa96e499e
Revises: d2111ab4a366
Create Date: 2021-09-05 12:37:11.825888

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '893aa96e499e'
down_revision = 'd2111ab4a366'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'search',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('child_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.Enum('random', 'brain', name='searchtype'), nullable=True),
        sa.Column('token', sa.Unicode(length=12), nullable=False),
        sa.ForeignKeyConstraint(
            ['child_id'], ['child.id'], name=op.f('search_child_id_child_fkey')
        ),
        sa.ForeignKeyConstraint(
            ['user_id'], ['user.id'], name=op.f('search_user_id_user_fkey')
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('search_pkey')),
    )
    op.create_index(op.f('search_token_idx'), 'search', ['token'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('search_token_idx'), table_name='search')
    op.drop_table('search')
    # ### end Alembic commands ###
