"""empty message

Revision ID: ff464a474c47
Revises: 98b0f899d267
Create Date: 2020-01-27 02:14:01.676830

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'ff464a474c47'
down_revision = '98b0f899d267'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        update need_family nf set paid = s.paid from (
            select sum(p.need_amount) as paid, p.id_need as in, p.id_user as iu
            from payment p
            where p.verified is not NULL group by p.id_need, id_user
        ) as s where s.in = nf.id_need and s.iu = nf.id_user;
    ''')

    op.execute('''
        update need n set donated = s.donated from (
            select sum(p.donation_amount) as donated, p.id_need as in
            from payment p
            where p.verified is not NULL group by p.id_need
        ) as s where s.in = n.id;
    ''')
    pass


def downgrade():
    pass
