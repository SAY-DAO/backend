"""empty message

Revision ID: 4fbd5bfb97bd
Revises: 23554e6d0034
Create Date: 2023-03-16 18:18:05.708589

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '4fbd5bfb97bd'
down_revision = '23554e6d0034'
branch_labels = None
depends_on = None


def upgrade():
    import say

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'child', sa.Column('adult_avatar_url', say.orm.types.ResourceURL(), nullable=True)
    )
    op.add_column('child', sa.Column('description', sa.String(), nullable=True))
    op.add_column(
        'child_version',
        sa.Column(
            'adult_avatar_url',
            say.orm.types.ResourceURL(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        'child_version',
        sa.Column(
            'adult_avatar_url_mod',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
        ),
    )
    op.add_column(
        'child_version',
        sa.Column('description', sa.String(), autoincrement=False, nullable=True),
    )
    op.add_column(
        'child_version',
        sa.Column(
            'description_mod',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('child_version', 'description_mod')
    op.drop_column('child_version', 'description')
    op.drop_column('child_version', 'adult_avatar_url_mod')
    op.drop_column('child_version', 'adult_avatar_url')
    op.drop_column('child', 'description')
    op.drop_column('child', 'adult_avatar_url')
    # ### end Alembic commands ###
