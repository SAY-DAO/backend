import os, shutil, copy

import redis
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
from say.date import *
from say.authorization import *
from say.roles import *
from say.exceptions import *
from say.langs import LANGS
from say.locale import ChangeLocaleTo, get_locale
from say.sms import MeliPayamak
from say.decorators import json
from say.orm import obj_to_dict
from .exception import HTTPException
from ..config import configs
from ..helpers import get_secret


DEFAULT_CHILD_ID = 104  # TODO: Remove this after implementing pre needs

basicConfig(level=configs.LOGLEVEL)
logger = getLogger('main')


# using pool_pre_ping to test the connection
# see https://docs.sqlalchemy.org/en/13/core/pooling.html#disconnect-handling-pessimistic
db = create_engine(configs.postgres_url, pool_pre_ping=True)

BASE_FOLDER = os.getcwd()

if not os.path.isdir(configs.UPLOAD_FOLDER):
    os.makedirs(configs.UPLOAD_FOLDER)

ALLOWED_VOICE_EXTENSIONS = {"wav", "m4a", "wma", "mp3", "aac", "ogg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_RECEIPT_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | {"pdf"}

# if configs.ENVIRONMENT != 'local':
sentry_sdk.init(
    dsn=configs.SENTRY_DSN,
    environment=configs.ENVIRONMENT,
    integrations=[
        FlaskIntegration(),
        SqlalchemyIntegration(),
        CeleryIntegration(),
        RedisIntegration(),
    ],
    traces_sample_rate=configs.SENTRY_SAMPLE_RATE,
    _experiments={"auto_enabling_integrations": True},
)

app = Flask(__name__)
# To disable flask_restful exception handler
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config.update(configs.to_dict())

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["SWAGGER"] = {
    # "swagger_version": "3.20.9",
    "specs": [
        {"version": "2.0", "title": "SAY API", "endpoint": "api_v2", "route": "/api/v2"}
    ]
}

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
redis_client = redis.Redis(configs.REDIS_HOST, configs.REDIS_PORT)
api = Api(app)


@app.before_first_request
def setup_i18n():
    from say.i18n import setup
    setup()


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    from say.models import session
    session.remove()
    return response_or_exc


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

