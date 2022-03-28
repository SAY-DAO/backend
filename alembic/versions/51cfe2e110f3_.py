"""empty message

Revision ID: 51cfe2e110f3
Revises: 0dc7eeb9c798
Create Date: 2022-03-28 22:23:17.080789

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '51cfe2e110f3'
down_revision = '0dc7eeb9c798'
branch_labels = None
depends_on = None


def upgrade():
    from say.models import Child
    from say.models import ChildMigration
    from say.orm import init_model
    from say.orm import session

    init_model(op.get_bind())

    for child in session.query(Child).filter(Child.migratedId.isnot(None)):
        migrated_child = session.query(Child).get(child.migratedId)

        migration = ChildMigration(
            child=child,
            new_sw_id=child.id_social_worker,
            old_sw_id=migrated_child.id_social_worker,
            migrated_at=child.migrateDate,
            new_generated_code=child.generatedCode,
            old_generated_code=migrated_child.generatedCode,
        )
        session.add(migration)

    session.commit()


def downgrade():
    pass
