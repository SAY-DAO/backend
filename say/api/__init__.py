import os, shutil, copy

import redis
from celery import Celery
from flask import (
    Flask,
    jsonify,
    json as _json,
    Response,
    request,
    Blueprint,
    send_from_directory,
    make_response,
    redirect,
)
from flask_restful import Api, Resource
from sqlalchemy import create_engine
from datetime import datetime
from flasgger import Swagger
from flasgger.utils import swag_from
from werkzeug.utils import secure_filename
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from logging import debug, basicConfig, DEBUG, getLogger
from flask_caching import Cache
from flask_cors import CORS
import flask_monitoringdashboard as dashboard
from mailerlite import MailerLiteApi
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from say.api.ext.jwt import jwt
from say.payment import IDPay
from say.celery import beat
from say.date import *
from say.authorization import *
from say.roles import *
from say.exceptions import *
from say.langs import LANGS
from say.locale import ChangeLocaleTo, get_locale
from say.sms import MeliPayamak
from say.decorators import json
from say.orm import obj_to_dict


ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
ADD_TO_HOME_URL = 'https://sayapp.company/add'
DEFAULT_CHILD_ID = 104  # TODO: Remove this after implementing pre needs

CELERY_TASK_LIST = [
    'say.tasks',
]

basicConfig(level=DEBUG)
logger = getLogger('main')

conf = {
    'dbUrl': 'postgresql://postgres:postgres@localhost/say_en'
}
try:
    with open("./config.json") as config_file:
        conf = _json.load(config_file)
except:
    pass

db_url = os.environ.get('DB')
if db_url:
    conf["dbUrl"] = db_url

# using pool_pre_ping to test the connection
# see https://docs.sqlalchemy.org/en/13/core/pooling.html#disconnect-handling-pessimistic
db = create_engine(conf["dbUrl"], pool_pre_ping=True)

BASE_FOLDER = os.getcwd()
UPLOAD_FOLDER = "files"

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

FLAGS = os.path.join(BASE_FOLDER, "say")
FLAGS = os.path.join(FLAGS, "flags")

ALLOWED_VOICE_EXTENSIONS = {"wav", "m4a", "wma", "mp3", "aac", "ogg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_RECEIPT_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | {"pdf"}

sentry_sdk.init(
    dsn=conf.get('SENTRY_DSN'),
    environment=ENVIRONMENT,
    integrations=[
        FlaskIntegration(),
        SqlalchemyIntegration(),
        CeleryIntegration(),
        RedisIntegration(),
    ],
    traces_sample_rate = conf.get('SENTRY_SAMPLE_RATE', 0.5),
    _experiments={"auto_enabling_integrations": True},
)

app = Flask(__name__)
app.config['ADD_TO_HOME_URL'] = ADD_TO_HOME_URL
app.config['JSON_SORT_KEYS'] = False
app.config['SET_PASSWORD_URL'] = 'setpassword'
app.config['RESET_PASSSWORD_EXPIRE_TIME'] = 2 * 3600 # 2 hours
app.config['RESET_PASSWORD_TOKEN_LENGTH'] = 8 # Chars
app.config['BASE_URL'] = 'http://0.0.0.0:5000/'
app.config['SQLALCHEMY_DATABASE_URI'] = conf['dbUrl']
app.config['SANDBOX'] = True
app.config['IDPAY_API_KEY'] = "83bdbfa4-04e6-4593-ba07-3e0652ae726d"
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["DEBUG"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DELIVER_TO_CHILD_DELAY"] = 4 * 60 * 60 # 4 hours
app.config["RATELIMIT_DEFAULT"] = "100 per minutes"
app.config['PAYMENT_ORDER_ID_LENGTH'] = 8
app.config['PRODUCT_UNPAYABLE_PERIOD'] = 3 # Days

app.config["MELI_PAYAMAK_USERNAME"] = "change-this"
app.config["MELI_PAYAMAK_PASSWORD"] = "change-this"
app.config["MELI_PAYAMAK_FROM"] = "chage-this"

app.config.update({
    "CACHE_TYPE": "redis", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
})
app.config["SWAGGER"] = {
    # "swagger_version": "3.20.9",
    "specs": [
        {"version": "2.0", "title": "SAY API", "endpoint": "api_v2", "route": "/api/v2"}
    ]
}

app.config.update({
    'JWT_ACCESS_TOKEN_EXPIRES': 24 * 3600, # 1 day
    'JWT_REFRESH_TOKEN_EXPIRES': 3 * 30 * 24 * 3600, # 3 months
    'JWT_BLACKLIST_ENABLED': True,
    'JWT_BLACKLIST_TOKEN_CHECKS': ['access', 'refresh'],
})

app.config.update({
    'REDIS_HOST': 'localhost',
    'REDIS_PORT': '6379',
    'REVOKED_TOKEN_STORE_DB': 1,
})

app.config['VERIFICATION_MAXAGE'] = 5  # minutes

app.config.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    redbeat_redis_url='redis://localhost:6379/0',
)

app.config.update(conf)


def create_celery_app(app):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.
    :param app: Flask app
    :return: Celery app
    """
    celery = Celery(app.import_name, broker=app.config['broker_url'],
                    include=CELERY_TASK_LIST)
    celery.conf.timezone = 'UTC'
    celery.conf.beat_schedule = beat
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class DBTask(TaskBase):
        _session = None

        def after_return(self, *args, **kwargs):
            if self._session is not None:
                self._session.close()
                self._session.remove()

        @property
        def session(self):
            if self._session is None:
                from say.models import session
                self._session = session

            return self._session

    celery.DBTask = DBTask

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = create_celery_app(app)

cache = Cache(app)

Swagger(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
)

mail = Mail(app)

jwt.init_app(app)

idpay = IDPay(app.config['IDPAY_API_KEY'], app.config['SANDBOX'])

sms_provider = MeliPayamak(
    app.config['MELI_PAYAMAK_USERNAME'],
    app.config['MELI_PAYAMAK_PASSWORD'],
    app.config['MELI_PAYAMAK_FROM'],
)

mailerlite = MailerLiteApi(app.config.get('MAILERLITE_API_KEY', 'not-entered'))

# try:
#     from say.basedata import basedata
#     basedata(db)
# except:
#     pass

api = Api(app)


def allowed_voice(filename):
    if (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_VOICE_EXTENSIONS
    ):
        return True

    raise TypeError('Wrong voice format')


def allowed_image(filename):
    if (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    ):
        return True

    raise TypeError('Wrong image format')


def allowed_receipt(filename):
    if (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_RECEIPT_EXTENSIONS
    ):
        return True

    raise TypeError('Wrong receipt format')

