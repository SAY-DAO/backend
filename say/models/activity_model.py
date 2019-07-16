from say.models.social_worker_model import SocialWorkerModel
from . import *

"""
Activity Model
"""


class ActivityModel(base):
    __tablename__ = 'activity'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    Id_social_worker = Column(Integer, ForeignKey(SocialWorkerModel.Id), nullable=False)
    ActivityCode = Column(Integer, nullable=False)

    social_worker = relationship('SocialWorkerModel', foreign_keys='ActivityModel.Id_social_worker')
