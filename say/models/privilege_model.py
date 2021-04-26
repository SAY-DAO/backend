from . import *


"""
Privilege Model
"""


class Privilege(base, Timestamp):
    __tablename__ = "social_worker_type"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    privilege = Column(Integer, nullable=False)
    # 1:super admin
    # 2:social worker
    # 3:coordinator
    # 4:NGO supervisor
    # 5:SAY supervisor
    # 6:admin
