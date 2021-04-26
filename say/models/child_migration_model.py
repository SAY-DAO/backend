from datetime import datetime

from sqlalchemy import func
from sqlalchemy_utils.models import Timestamp

from . import *


class ChildMigration(base):
    __tablename__ = 'child_migration'

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('child.id'), nullable=False)
    new_sw_id = Column(Integer, ForeignKey('social_worker.id'), nullable=False)
    old_sw_id = Column(Integer, ForeignKey('social_worker.id'), nullable=False)

    new_generated_code = Column(String, nullable=False)
    old_generated_code = Column(String, nullable=False)

    migrated_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    child = relationship(
        'Child',
        uselist=False,
        foreign_keys=child_id,
        back_populates='migrations',
    )

    new_sw = relationship(
        'SocialWorker',
        uselist=False,
        foreign_keys=new_sw_id,
    )

    old_sw = relationship(
        'SocialWorker',
        uselist=False,
        foreign_keys=old_sw_id,
    )
