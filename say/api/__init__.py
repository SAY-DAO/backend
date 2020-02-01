import os, shutil, copy, json

from celery import Celery
from flask import (
    Flask,
    jsonify,
    json,
    Response,
    request,
    Blueprint,
    send_from_directory,
    make_response,
    redirect,
    render_template,
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

from ..payment import IDPay
from say.celery import beat
from say.date import *
from say.authorization import *
from say.roles import *
from say.exceptions import *
from say.langs import LANGS
from say.locale import ChangeLocaleTo, get_locale


DEFAULT_CHILD_ID = 104  # TODO: Remove this after implementing pre needs

CELERY_TASK_LIST = [
    'say.tasks',
]

basicConfig(level=DEBUG)

conf = {
    'dbUrl': 'postgresql://postgres:postgres@localhost/say_en'
}
try:
    with open("./config.json") as config_file:
        conf = json.load(config_file)
except:
    pass

db = create_engine(conf["dbUrl"])

BASE_FOLDER = os.getcwd()

UPLOAD_FOLDER = "files"

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

FLAGS = os.path.join(BASE_FOLDER, "say")
FLAGS = os.path.join(FLAGS, "flags")

ALLOWED_VOICE_EXTENSIONS = {"wav", "m4a", "wma", "mp3", "aac", "ogg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_RECEIPT_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | {"pdf"}

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SET_PASSWORD_URL'] = 'setpassword'
app.config['RESET_PASSSWORD_EXPIRE_TIME'] = 2 * 3600 # 2 hours
app.config['BASE_URL'] = 'http://0.0.0.0:5000/'
app.config['SQLALCHEMY_DATABASE_URI'] = conf['dbUrl']
app.config['SANDBOX'] = True
app.config['IDPAY_API_KEY'] = "83bdbfa4-04e6-4593-ba07-3e0652ae726d"
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["DEBUG"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DELIVER_TO_CHILD_DELAY"] = 4 * 60 * 60 # 4 hours
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

app.config['VERIFICATION_EMAIL_MAXAGE'] = 2 # minutes

app.config.update(
    broker_url='redis://localhost:6379/0',
    result_backend='rpc://',
    redbeat_redis_url = "redis://localhost:6379/0"
)

app.config.update(conf)


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.
    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

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
    default_limits=["100 per minute"],
)

mail = Mail(app)

jwt = JWTManager(app)

idpay = IDPay(app.config['IDPAY_API_KEY'], app.config['SANDBOX'])

from say.basedata import basedata

try:
    basedata(db)
except:
    pass

api = Api(app)
# api_bp = Blueprint('api', __name__)
# api = Api(api_bp)



def render_template(path, *args, locale=None, date_with_year=True,
                    **kwargs):

    from flask import render_template
    from say.formatters import int_formatter, expose_datetime

    if not locale:
        return render_template(path, *args, int_formatter=int_formatter, **kwargs)

    # locale is str or Locale object, so we need to make sure it is str
    locale = str(locale) or get_locale()
    with ChangeLocaleTo(locale):
        locale_path = os.path.join(locale, path)
        for k, v in kwargs.items():
            if isinstance(v, datetime):
                kwargs[k] = expose_datetime(
                    v,
                    locale=locale,
                    with_year=date_with_year,
                )

        return render_template(
            locale_path,
            *args,
            int_formatter=int_formatter,
            **kwargs
        )


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


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    from ..models.revoked_token_model import RevokedToken
    from sqlalchemy.orm import scoped_session, sessionmaker
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=db)
    )
    return RevokedToken.is_jti_blacklisted(jti, session)

