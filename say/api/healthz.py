from healthcheck import HealthCheck

from ..app import app
from .ext import redis_client
from ..orm import session

health = HealthCheck(
    app, 
    '/api/healthz',
    success_ttl=None, 
    failed_ttl=None,
)


def redis_available():
    info = redis_client.info()
    return True, f'redis ok: {info}'


health.add_check(redis_available)


def postgres_avaliable():
    result = session.bind.execute('SELECT * from alembic_version')
    alembic_version = [dict(row) for row in result][0]['version_num']
    return True, f'postgres ok, alembic_version: {alembic_version}'


health.add_check(postgres_avaliable)
