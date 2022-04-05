from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy.orm import relationship

from . import base


class Country(base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)

    iso3 = Column(Unicode(3))
    numeric_code = Column(Unicode(3))
    iso2 = Column(Unicode(4))
    phone_code = Column(Unicode(255))
    capital = Column(Unicode(255))
    currency = Column(Unicode(255))
    currency_name = Column(Unicode(255))
    currency_symbol = Column(Unicode(255))
    tld = Column(Unicode(255))
    native = Column(Unicode(255))
    region = Column(Unicode(255))
    subregion = Column(Unicode(255))
    timezones = Column(UnicodeText)
    translations = Column(UnicodeText)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    emoji = Column(Unicode(191))
    emojiU = Column('emojiu', Unicode(191))
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

    states = relationship('State', back_populates='country')
    cities = relationship('City', back_populates='country')


@sa.event.listens_for(Country, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    # When a model with a timestamp is updated; force update the updated
    # timestamp.
    target.updated_at = datetime.utcnow()
