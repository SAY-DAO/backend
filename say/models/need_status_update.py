from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy_utils import Timestamp

from say.orm import base


class NeedStatusUpdate(base, Timestamp):
    __tablename__ = 'need_status_updates'

    id = Column(Integer, primary_key=True)
    need_id = Column(Integer, ForeignKey('need.id'))
    sw_id = Column(Integer, ForeignKey('social_worker.id'))
    old_status = Column(Integer)
    new_status = Column(Integer)

    need = relationship(
        'Need',
        foreign_keys=need_id,
        uselist=False,
        back_populates='status_updates',
    )

    sw = relationship(
        'SocialWorker',
        foreign_keys=sw_id,
        uselist=False,
        back_populates='need_status_updates',
    )
