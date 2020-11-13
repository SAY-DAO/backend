from sqlalchemy.sql.schema import Column
from sqlalchemy import Unicode
from sqlalchemy.orm import relationship
from sqlalchemy_utils import Timestamp

from say.orm import base


class NakamaOwner(base, Timestamp):
    __tablename__ = 'nakama_owners'

    address = Column(Unicode(64), primary_key=True)

    nakama_txs = relationship('NakamaTx', back_populates='nakama_owner')
