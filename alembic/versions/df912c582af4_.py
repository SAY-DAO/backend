"""empty message

Revision ID: df912c582af4
Revises: c0c97e8069b3
Create Date: 2019-12-02 16:42:48.884405

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'df912c582af4'
down_revision = 'c0c97e8069b3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        ALTER TABLE ngo
        ADD CONSTRAINT ngo_coordinator_id_fkey FOREIGN KEY ("coordinatorId")
            REFERENCES social_worker (id)
            ON DELETE CASCADE;
    ''')


def downgrade():
    pass
