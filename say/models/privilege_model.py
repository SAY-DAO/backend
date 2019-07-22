from . import *

"""
Privilege Model
"""


class PrivilegeModel(base):
    __tablename__ = 'social_worker_type'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    Name = Column(String, nullable=False)
    Privilege = Column(Integer, nullable=False)
