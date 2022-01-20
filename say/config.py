import os
from logging import DEBUG as DEBUG_LVL

from dotenv import find_dotenv
from dotenv import load_dotenv

from say.helpers import get_secret


class Config(object):
    ENVIRONMENT = 'local'
    PRODUCTION = False
    TESTING = True
    DEBUG = True
    LOGLEVEL = DEBUG_LVL
    POSTGRES_HOST = 'db'
    POSTGRES_PORT = '5432'
    POSTGRES_DB = 'say'
    POSTGRES_TEST_DB = 'say_test'
    POSTGRES_ADMIN_DB = 'postgres'
    POSTGRES_USER = 'postgres'
    POSTGRES_PASSWORD = 'postgres'
    BASE_URL = 'http://0.0.0.0:3100'
    API_URL = 'http://0.0.0.0:5000'
    BASE_RESOURCE_URL = API_URL
    REDIS_HOST = 'redis'
    ADD_TO_HOME_URL = 'https://sayapp.company/add'
    UPLOAD_FOLDER = 'files'
    REDIS_PORT = '6379'
    JWT_SECRET_KEY = 'axcasdxaobisduba'
    REVOKED_TOKEN_STORE_HOST = 'redis'
    REVOKED_TOKEN_STORE_PORT = '6379'
    REVOKED_TOKEN_STORE_DB = 1
    SANDBOX = True
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
    CACHE_REDIS_HOST = 'redis'
    CACHE_DEFAULT_TIMEOUT = 300
    SENTRY_DSN = 'https://e7665a883afe47d082b3fa4e0b956c07@sentry.say.company/4'
    INFURA_URL = 'https://mainnet.infura.io/v3/0be880209fd94507a2b7b340f638f8a0'
    NAKAMA_ADDRESS = '0x052e909bd1a6b20d35c850d2a188fd515a738953'
    ORPHAN_NAKAMA_TX_RANGE = 2  # Days
    MAILERLITE_API_KEY = 'abcd'
    MAILERLITE_GROUP_ID = '0'
    INVITATION_URL = '/search-result?token=%s'
    INVITATION_V3_URL = '/invitations/%s'
    MAIL_DEFAULT_SENDER = 'devtest@say.company'

    # Business
    MIN_BANK_AMOUNT = 1000  # Toman
    RANDOM_SEARCH_FACTOR = 3
    REQUEST_CACHE_MAX_SIZE = 1024
    REQUEST_CACHE_TTL = 30 * 60  # 30 minutes

    # Celery
    BROKER = 'redis'
    task_soft_time_limit = 60
    task_acks_late = True
    worker_prefetch_multiplier = 1

    FAMILY_REPORT_EMAIL = 'vfamily@say.company'

    # Pagination
    PAGINATION_TAKE_HEADER_KEY = 'X-Take'
    PAGINATION_SKIP_HEADER_KEY = 'X-Skip'
    PAGINATION_DEFAULT_TAKE = 50
    PAGINATION_MAX_TAKE = 500

    POSTRGES_MAX_BIG_INT = 9223372036854775807

    def __init__(self):
        load_dotenv(find_dotenv())
        for k, v in os.environ.items():
            if not k.startswith('SAY_'):
                continue
            key = k.replace('SAY_', '')
            v = self._cast(v)

            setattr(self, key, v)

        self.POSTGRES_PASSWORD = get_secret(
            'postgres-password',
            self.POSTGRES_PASSWORD,
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
        return (
            f'postgresql://'
            f'{self.POSTGRES_USER}'
            f':{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}'
            f':{self.POSTGRES_PORT}'
            f'/{self.POSTGRES_DB}'
        )

    @property
    def postgres_test_url(self):
        return (
            f'postgresql://'
            f'{self.POSTGRES_USER}'
            f':{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}'
            f':{self.POSTGRES_PORT}'
            f'/{self.POSTGRES_TEST_DB}'
        )

    @property
    def postgres_admin_url(self):
        return (
            f'postgresql://'
            f'{self.POSTGRES_USER}'
            f':{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}'
            f':{self.POSTGRES_PORT}'
            f'/{self.POSTGRES_ADMIN_DB}'
        )

    @property
    def redis_url(self):
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    @property
    def broker_url(self):
        return f'{self.redis_url}/0'

    @property
    def result_backend(self):
        return f'{self.redis_url}/0'

    @property
    def redbeat_redis_url(self):
        return f'{self.redis_url}/0'

    def to_dict(self):
        return dict(
            (key, getattr(self, key))
            for key in dir(self)
            if not key.startswith('__') and not callable(getattr(self, key))
        )


configs: Config = Config()
