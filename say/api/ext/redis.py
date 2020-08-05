import redis

from say.config import config

revoked_store = redis.StrictRedis(
    host=config['REDIS_HOST'],
    port=config['REDIS_PORT'],
    db=config['REVOKED_TOKEN_STORE_DB'],
    decode_responses=True,
)