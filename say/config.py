from logging import DEBUG
from pathlib import Path  # Python 3.6+ only
import os

from dotenv import load_dotenv, find_dotenv

conf = {
    'PRODUCTION': False,
    'TESTING': False,
    "DEBUG": True,
    'LOGLEVEL': DEBUG,
    'BASE_URL': '0.0.0.0:3100',
    'API_URL': '0.0.0.0:5000',
    'DB_URL': 'postgresql://postgres:postgres@localhost/say_tmp',
    'REDIS_HOST': 'localhost',
    'ADD_TO_HOME_URL': 'https://sayapp.company/add',
    'UPLOAD_FOLDER': 'files',
    'REDIS_PORT': '6379',
    'REVOKED_TOKEN_STORE_DB': 1,
    'JWT_SECRET_KEY': 'axcasdxaobisduba',
    'REVOKED_TOKEN_STORE': {
        'host': 'localhost',
        'port': 6379,
        'db': 1,
    },
    'SANDBOX': True,
    'JSON_SORT_KEYS': False,
    'SET_PASSWORD_URL': 'setpassword',
    'RESET_PASSWORD_EXPIRE_TIME': 2 * 3600,
    'RESET_PASSWORD_TOKEN_LENGTH': 8,
    'IDPAY_API_KEY': "83bdbfa4-04e6-4593-ba07-3e0652ae726d",
    "DELIVER_TO_CHILD_DELAY": 4 * 60 * 60,
    "RATELIMIT_DEFAULT": "100 per minutes",
    'PAYMENT_ORDER_ID_LENGTH': 8,
    'PRODUCT_UNPAYABLE_PERIOD': 7,
    'MELI_PAYAMAK_USERNAME': 'change-this',
    'MELI_PAYAMAK_PASSWORD': 'change-this',
    'MELI_PAYAMAK_FROM': 'change-this',
    'VERIFICATION_MAXAGE': 5,
    'JWT_ACCESS_TOKEN_EXPIRES': 24 * 3600,  # 1 day
    'JWT_REFRESH_TOKEN_EXPIRES': 3 * 30 * 24 * 3600,  # 3 months
    'JWT_BLACKLIST_ENABLED': True,
    'JWT_BLACKLIST_TOKEN_CHECKS': ['access', 'refresh'],
    'BROKER_URL': 'redis://localhost:6379/0',
    'RESULT_BACKEND': 'redis://localhost:6379/0',
    'REDBEAT_REDIS_URL': "redis://localhost:6379/0",
    "CACHE_TYPE": "redis",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
}


def load_config(**kwargs):
    load_dotenv(find_dotenv())

    for k, v in os.environ.items():
        conf[k] = v

    conf.update(kwargs)
    return conf


config = load_config()
