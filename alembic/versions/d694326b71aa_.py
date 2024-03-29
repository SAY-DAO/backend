"""empty message

Revision ID: d694326b71aa
Revises: 3b76dac2c5a7
Create Date: 2022-01-20 14:47:19.965173

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'd694326b71aa'
down_revision = '3b76dac2c5a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'user_family', sa.Column('is_participated', sa.Boolean(), nullable=True)
    )
    op.execute(
        '''
        update user_family uff set is_participated = (select count(nf.id)::int::bool from user_family uf left join need_family nf on
        nf.id_family = uf.id_family and nf.id_user = uf.id_user where uf.id_family = uff.id_family and uf.id_user = uff.id_user);
        '''
    )
    op.execute('ALTER TABLE user_family ALTER COLUMN is_participated SET NOT NULL;')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_family', 'is_participated')
    # ### end Alembic commands ###
