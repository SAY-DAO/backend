from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.ext.hybrid import hybrid_property


class ActivateMixin:
    is_active = Column(Boolean, default=True, nullable=False)

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def toggle_active(self):
        self.is_active = not self.is_active

    @hybrid_property
    def isActive(self):
        return self.is_active

    @isActive.expression
    def isActive(cls):
        return cls.is_active

    @isActive.setter
    def isActive(cls, value):
        cls.is_active = value
