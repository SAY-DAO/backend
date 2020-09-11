from healthcheck import HealthCheck, EnvironmentDump

from . import app, redis_client, db
from ..config import configs

# wrap the flask app and give a heathcheck url
health = HealthCheck(
    app, 
    '/api/healthz',
    success_ttl=None, 
    failed_ttl=None,
)

def redis_available():
    info = redis_client.info()
    return True, 'redis ok'

health.add_check(redis_available)


def postgres_avaliable():
    result = db.execute('SELECT * from alembic_version')
    alembic_version = [dict(row) for row in result][0]['version_num']
    return True, f'postgres ok, alembic_version: {alembic_version}'
    
health.add_check(postgres_avaliable)
