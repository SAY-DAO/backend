from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from . import *


'''
Activity Model
'''


class Activity(base, Timestamp):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_social_worker = Column(Integer, ForeignKey('social_worker.id'), nullable=False)
    activityCode = Column(Integer, nullable=False)
    diff = Column(JSONB, nullable=True)
    model = Column(Text)
    # 11: update profile                 21: add user                    31: delete user                    4: payment
    # 12: update child                   22: add child                   32: delete child                   5: need done
    # 13: update need                    23: add need                    33: delete need
    # 14: update social worker           24: add privilege               34: delete privilege
    # 15: update privilege               25: add ngo                     35: delete ngo
    # 16: update ngo                     26: add need type (category)    36: delete need type (category)
    # 17: update need type (category)    27: add receipt                 37: delete receipt
    # 18: update receipt

    social_worker = relationship(
        'SocialWorker',
        foreign_keys='Activity.id_social_worker',
    )
