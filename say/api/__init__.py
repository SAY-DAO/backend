import os, shutil, copy

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
from logging import debug, basicConfig, DEBUG
from flask_caching import Cache
from flask_cors import CORS
import flask_monitoringdashboard as dashboard
from mailerlite import MailerLiteApi

from say.api.ext.jwt import jwt
from say.config import config
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


DEFAULT_CHILD_ID = 104  # TODO: Remove this after implementing pre needs

CELERY_TASK_LIST = [
    'say.tasks',
]

basicConfig(level=config['LOGLEVEL'])

# using pool_pre_ping to test the connection
# see https://docs.sqlalchemy.org/en/13/core/pooling.html#disconnect-handling-pessimistic
db = create_engine(config["DB_URL"], pool_pre_ping=True)

BASE_FOLDER = os.getcwd()

if not os.path.isdir(config['UPLOAD_FOLDER']):
    os.makedirs(config['UPLOAD_FOLDER'])

FLAGS = os.path.join(BASE_FOLDER, "say")
FLAGS = os.path.join(FLAGS, "flags")

ALLOWED_VOICE_EXTENSIONS = {"wav", "m4a", "wma", "mp3", "aac", "ogg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_RECEIPT_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | {"pdf"}

app = Flask(__name__)
app.config.update(config)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
SWAGGER = {
    # "swagger_version": "3.20.9",
    "specs": [
        {
            "version": "2.0",
            "title": "SAY API",
            "endpoint": "api_v2",
            "route": "/v2",
         }

    ]
}


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.
    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name, broker=app.config['BROKER_URL'],
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

APIMD_CONFIG_FILE_PROD = 'apimd-config-prod.cfg'
APIMD_CONFIG_FILE = 'apimd-config.cfg'
if config['PRODUCTION']:
    if not os.path.isfile(APIMD_CONFIG_FILE_PROD):
        raise Exception('''
            Make sure apimd-config-prod.cfg exist
            and admin PASSWORD, CUSTOM_LINK, SECURITY_TOKEN and DATABASE
            are correctly set in apimd-config-prod.cfg
        ''')

    dashboard.config.init_from(file=APIMD_CONFIG_FILE_PROD)
else:
    dashboard.config.init_from(file=APIMD_CONFIG_FILE)
    print(
        'Open http://localhost/dashboard and use admin admin to see '
        'API monitoring dashboard'
    )

try:
    dashboard.bind(app)
except Exception as e:
    print('''
        Make sure apimd-config-prod.cfg exist
        and admin PASSWORD, CUSTOM_LINK, SECURITY_TOKEN and DATABASE
        are correctly set in apimd-config-prod.cfg
        '''
    )
    raise

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

