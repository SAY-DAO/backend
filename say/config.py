import os
from logging import DEBUG

from dotenv import find_dotenv
from dotenv import load_dotenv

from say.helpers import get_secret


class Config(object):
    ENVIRONMENT = 'local'
    PRODUCTION = False
    TESTING = False
    DEBUG = True
    LOGLEVEL = DEBUG
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = '5432'
    POSTGRES_DB = 'say'
    POSTGRES_USER = 'postgres'
    POSTGRES_PASSWORD = 'postgres'
    BASE_URL = 'http://0.0.0.0:3100'
    API_URL = 'http://0.0.0.0:5000'
    REDIS_HOST = 'localhost'
    ADD_TO_HOME_URL = 'https://sayapp.company/add'
    UPLOAD_FOLDER = 'files'
    REDIS_PORT = '6379'
    JWT_SECRET_KEY = 'axcasdxaobisduba'
    REVOKED_TOKEN_STORE_HOST = 'localhost'
    REVOKED_TOKEN_STORE_PORT = '6379'
    REVOKED_TOKEN_STORE_DB = 1
    SANDBOX = False
    JSON_SORT_KEYS = False
    SET_PASSWORD_URL = 'setpassword'
    RESET_PASSWORD_EXPIRE_TIME = 2 * 3600
    RESET_PASSWORD_TOKEN_LENGTH = 8
    IDPAY_API_KEY = 'change-this'
    DELIVER_TO_CHILD_DELAY = 4 * 60 * 60
    RATELIMIT_DEFAULT = '100 per minutes'
    PAYMENT_ORDER_ID_LENGTH = 8
    PRODUCT_UNPAYABLE_PERIOD = 7
    MELI_PAYAMAK_USERNAME = 'change-this'
    MELI_PAYAMAK_PASSWORD = 'change-this'
    MELI_PAYAMAK_FROM = 'change-this'
    VERIFICATION_MAXAGE = 30
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 3600  # 1 day
    JWT_REFRESH_TOKEN_EXPIRES = 3 * 30 * 24 * 3600  # 3 months
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    CACHE_TYPE = 'redis'  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 300
    RABBITMQ_DEFAULT_USER = 'guest'
    RABBITMQ_DEFAULT_PASS = 'guest'
    RABBITMQ_VHOST = 'say'
    RABBITMQ_HOST = 'localhost'
    RABBITMQ_PORT = '5672'
    SENTRY_DSN = 'https://e7665a883afe47d082b3fa4e0b956c07@sentry.say.company/4'
    INFURA_URL = 'https://mainnet.infura.io/v3/0be880209fd94507a2b7b340f638f8a0'
    NAKAMA_ADDRESS =  '0x052e909bd1a6b20d35c850d2a188fd515a738953'
    ORPHAN_NAKAMA_TX_RANGE = 2 # Days
    MAILERLITE_API_KEY = 'abcd'

    # Celery
    BROKER = 'redis'
    task_soft_time_limit = 60
    task_acks_late = True
    worker_prefetch_multiplier = 1

    FAMILY_REPORT_EMAIL = 'vfamily@say.company'

    def __init__(self):
        load_dotenv(find_dotenv())
        for k, v in os.environ.items():
            if not k.startswith('SAY_'):
                continue
            key = k.replace('SAY_', '')
            v = self._cast(v)

            setattr(self, key, v)

        self.POSTGRES_PASSWORD = get_secret(
            'postgres-password', self.POSTGRES_PASSWORD,
        )
        self.RABBITMQ_DEFAULT_PASS = get_secret(
            'rabbitmq-password', self.RABBITMQ_DEFAULT_PASS,
        )

    def _cast(self, v):
        try:
            v = float(v)
            if v.is_integer():
                v = int(v)
        except ValueError:
            if v == 'false':
                v = False
            elif v == 'true':
                v = True
            elif v == 'null' or v == 'None':
                v = None
            else:
                pass

        return v

    @property
    def postgres_url(self):
        return f'postgresql://' \
            f'{self.POSTGRES_USER}' \
            f':{self.POSTGRES_PASSWORD}' \
            f'@{self.POSTGRES_HOST}' \
            f':{self.POSTGRES_PORT}' \
            f'/{self.POSTGRES_DB}'

    @property
    def redis_url(self):
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    @property
    def rabbitmq_url(self):
        return f'amqp://' \
           f'{self.RABBITMQ_DEFAULT_USER}' \
           f':{self.RABBITMQ_DEFAULT_PASS}' \
           f'@{self.RABBITMQ_HOST}' \
           f':{self.RABBITMQ_PORT}' \
           f'/{self.RABBITMQ_VHOST}'

    @property
    def broker_url(self):
        if self.BROKER == 'redis':
            return f'{self.redis_url}/0'
        elif self.BROKER == 'rabbitmq':
            return self.rabbitmq_url

    @property
    def result_backend(self):
        if self.BROKER == 'redis':
            return f'{self.redis_url}/0'
        elif self.BROKER == 'rabbitmq':
            return 'rpc://'

    @property
    def redbeat_redis_url(self):
        return f'{self.redis_url}/0'

    def to_dict(self):
        return dict(
            (key, getattr(self, key))
            for key in dir(self)
            if not key.startswith('__') and not callable(getattr(self, key))
        )


configs = Config()
