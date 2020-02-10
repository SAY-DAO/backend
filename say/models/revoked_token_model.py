from . import *

"""
Revoke Token Model
"""

class RevokedToken(base):
    __tablename__ = 'revoked_tokens'
    id = Column(Integer, primary_key = True)
    jti = Column(String(120), index=True)

    @classmethod
    def is_jti_blacklisted(cls, jti, session):
        query = session.query(cls).filter_by(jti = jti).one_or_none()
        return bool(query)
