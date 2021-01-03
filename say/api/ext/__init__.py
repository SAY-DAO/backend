from logging import getLogger

import redis
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