"""empty message

Revision ID: e057440bc359
Revises: 1edf57319173
Create Date: 2020-01-06 20:19:21.558511

"""
from alembic import op
import sqlalchemy as sa

from say.models import session
from say.models import ChildModel


# revision identifiers, used by Alembic.
revision = 'e057440bc359'
down_revision = '1edf57319173'
branch_labels = None
depends_on = None


def upgrade():
    children = session.query(ChildModel)
    for c in children:
        c.sayname_translations = dict(en=c.sayName, fa=c.sayName_fa)
        c.bio_translations = dict(en=c.bio, fa=c.bio_fa)
        c.bio_summary_translations = dict(en=c.bioSummary, fa=c.bioSummary_fa)

    session.commit()

    op.drop_column('child', 'bio')
    op.drop_column('child', 'bioSummary')
    op.drop_column('child', 'sayName')

    # ### end Alembic commands ###


def downgrade():
    pass
