"""empty message

Revision ID: 22774c633395
Revises: 8a0bca2890cc
Create Date: 2020-11-12 19:53:05.067925

"""
from datetime import datetime

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '22774c633395'
down_revision = '8a0bca2890cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_nakama', sa.Boolean(), nullable=True))
    op.execute('UPDATE "user" set is_nakama = false;')
    op.execute('ALTER TABLE "user" ALTER COLUMN is_nakama SET NOT NULL;')
    op.execute('ALTER TABLE "user" ALTER COLUMN is_nakama SET DEFAULT false;')
    op.execute('COMMIT;')

    from say.models import User
    from say.orm import session

    nakama = User(
        firstName='SAY',
        lastName='Nakama',
        userName='nakama',
        avatarUrl=None,
        emailAddress='nakama@say.company',
        is_email_verified=True,
        gender=None,
        city=0,
        birthDate=None,
        birthPlace=None,
        lastLogin=datetime.utcnow(),
        password='password',
        locale='EN',
        phone_number=None,
        country=0,
        is_installed=True,
        is_nakama=True,
    )
    session.add(nakama)
    session.commit()

    # ### end Alembic commands ###


def downgrade():
    from say.models import User
    from say.orm import session

    session.query(User).filter(
        User.is_nakama == True,
    ).delete()
    session.commit()

    op.drop_column('user', 'is_nakama')

    # ### end Alembic commands ###
