from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.ext.hybrid import hybrid_property


class ActivateMixin:
    is_active = Column(Boolean, default=True, nullable=False)

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def toggle_active(self):
        self.is_active = not self.is_active


class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True)

    def delete(self):
        self.deleted_at = datetime.utcnow()

    def undelete(self):
        self.deleted_at = None

    @hybrid_property
    def is_deleted(self):
        return self.deleted_at is not None

    @is_deleted.expression
    def is_deleted(cls):
        return cls.deleted_at.isnot(None)

    @is_deleted.setter
    def is_deleted(self, value):
        if value:
            self.delete()
        else:
            self.undelete()
