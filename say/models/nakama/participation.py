from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Unicode
from ..need_family_model import NeedFamily


class NakamaParticipation(NeedFamily):
    address = Column(Unicode(64), ForeignKey('nakama_owners.address'), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'nakama'
    }