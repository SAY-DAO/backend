import redis

from say.config import config

revoked_store = redis.StrictRedis(
    host=config['REVOKED_TOKEN_STORE']['host'],
    port=config['REVOKED_TOKEN_STORE']['port'],
    db=config['REVOKED_TOKEN_STORE']['db'],
    decode_responses=True,
)