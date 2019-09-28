from . import *

"""
Privilege Model
"""


class PrivilegeModel(base):
    __tablename__ = "social_worker_type"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    privilege = Column(Integer, nullable=False)
    # 0:super admin
    # 1:social worker
    # 2:coordinator
    # 3:NGO supervisor
    # 4:SAY supervisor
    # 5:admin
