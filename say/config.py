import os
import json


conf = {
    'dbUrl': 'postgresql://postgres:postgres@localhost/say_en',
    'SQLALCHEMY_DATABASE_URI': conf['dbUrl'],
    'SANDBOX': True,
    'ADD_TO_HOME_URL': 'https://sayapp.company/add',
    'JSON_SORT_KEYS': False,
    'SET_PASSWORD_URL': 'setpassword',
    'RESET_PASSSWORD_EXPIRE_TIME': 2 * 3600,
    'RESET_PASSWORD_TOKEN_LENGTH': 8,
    'BASE_URL': 'http://0.0.0.0:5000/',
    'IDPAY_API_KEY': "83bdbfa4-04e6-4593-ba07-3e0652ae726d",
    "DEBUG": False,
    "UPLOAD_FOLDER": UPLOAD_FOLDER,
    "DELIVER_TO_CHILD_DELAY": 4 * 60 * 60,
    "RATELIMIT_DEFAULT": "100 per minutes",
    'PAYMENT_ORDER_ID_LENGTH': 8,
    'PRODUCT_UNPAYABLE_PERIOD': 3,
    'MELI_PAYAMAK_USERNAME': 'change-this',
    'MELI_PAYAMAK_PASSWORD': 'change-this',
    'MELI_PAYAMAK_FROM': 'change-this',
    'VERIFICATION_MAXAGE': 5,
    "SWAGGER": {
      # "swagger_version": "3.20.9",
      "specs": [{
          "version": "2.0", "title": "SAY API",
          "endpoint": "api_v2", "route": "/api/v2",
      }],
    },
    'JWT_ACCESS_TOKEN_EXPIRES': 24 * 3600,  # 1 day
    'JWT_REFRESH_TOKEN_EXPIRES': 3 * 30 * 24 * 3600,  # 3 months
    'JWT_BLACKLIST_ENABLED': True,
    'JWT_BLACKLIST_TOKEN_CHECKS': ['access', 'refresh'],
    'broker_url': 'redis://localhost:6379/0',
    'result_backend': 'redis://localhost:6379/0',
    'redbeat_redis_url': "redis://localhost:6379/0",

    "CACHE_TYPE": "redis",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
}

def load_config(config_file_url=None, **kwargs):
    if config_file_url:
        try:
            with open(config_file_url) as config_file:
                conf.update(json.load(config_file))
        except:
            pass

    db_url = os.environ.get('DB')
    if db_url:
        conf["dbUrl"] = db_url

    conf.update(kwargs)
    return conf


config = load_config('./config.json')
