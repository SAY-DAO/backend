from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import Unicode
from sqlalchemy.orm import relationship

from . import base


class City(base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256), nullable=False)

    state_id = Column(
        Integer,
        ForeignKey('states.id'),
        nullable=False,
    )
    state_code = Column(Unicode(255), nullable=False)
    state_name = Column(Unicode(255), nullable=False)

    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    country_code = Column(Unicode(2), nullable=False)
    country_name = Column(Unicode(255), nullable=False)

    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)

    flag = Column(SmallInteger, default='1')
    wikiDataId = Column('wikidataid', Unicode(255), default='Rapid API GeoDB Cities')

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    country = relationship('Country', back_populates='cities', foreign_keys=country_id)
    state = relationship('State', back_populates='cities', foreign_keys=state_id)


@sa.event.listens_for(City, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    # When a model with a timestamp is updated; force update the updated
    # timestamp.
    target.updated_at = datetime.utcnow()
