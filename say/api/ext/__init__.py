from logging import getLogger

import redis
from flask import request
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_restful import Api
from mailerlite import MailerLiteApi

from say.config import configs
from say.payment import IDPay
from say.sms import MeliPayamak


api = Api()
jwt = JWTManager()
idpay = IDPay(configs.IDPAY_API_KEY, configs.SANDBOX)
sms_provider = MeliPayamak(
    configs.MELI_PAYAMAK_USERNAME,
    configs.MELI_PAYAMAK_PASSWORD,
    configs.MELI_PAYAMAK_FROM,
)
mailerlite = MailerLiteApi(configs.MAILERLITE_API_KEY)
redis_client = redis.Redis(configs.REDIS_HOST, configs.REDIS_PORT)
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
logger = getLogger('main')


CLOUDFLARE_IP_HEADER_KEY = 'Cf-Connecting-Ip'


def get_remote_address():

    """
    :return: the ip address for the current request
     (or 127.0.0.1 if none found)

    """
    return (
        request.headers.get(CLOUDFLARE_IP_HEADER_KEY)
        or request.remote_addr
        or '127.0.0.1'
    )


def setup_healthz(app):
    from healthcheck import HealthCheck

    from say.orm import session

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
        result = session.bind.execute('SELECT * from alembic_version;')
        alembic_version = [dict(row) for row in result][0]['version_num']
        return True, f'postgres ok, alembic_version: {alembic_version}'

    health.add_check(postgres_avaliable)
