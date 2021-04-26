"""+ need_family user_avatar

Revision ID: f069672405c4
Revises: 708fca15d89d
Create Date: 2020-02-06 22:59:08.737315

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'f069672405c4'
down_revision = '708fca15d89d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('need_family', sa.Column('user_avatar', sa.Text(), nullable=True))
    op.execute('''
        UPDATE need_family nf
        SET user_avatar = u."avatarUrl"
        FROM "user" u
        WHERE nf.id_user = u.id;
    ''')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('need_family', 'user_avatar')
    # ### end Alembic commands ###
