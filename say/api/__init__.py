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
from sqlalchemy import create_engine, inspect, or_, not_, and_, func
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from datetime import datetime
from flasgger import Swagger
from flasgger.utils import swag_from
from werkzeug.utils import secure_filename
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from logging import debug, basicConfig, DEBUG
from flask_caching import Cache
from flask_cors import CORS

from ..payment import IDPay
from say.celery import beat
from say.date import *
from say.authorization import *
from say.roles import *
from say.exceptions import *


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

session_factory = sessionmaker(db)
session = scoped_session(session_factory)
base = declarative_base()
base.metadata.bind = db

BASE_FOLDER = os.getcwd()

UPLOAD_FOLDER = "files"

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

FLAGS = os.path.join(BASE_FOLDER, "say")
FLAGS = os.path.join(FLAGS, "flags")

ALLOWED_VOICE_EXTENSIONS = {"wav", "m4a", "wma", "mp3", "aac", "ogg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['BASE_URL'] = 'https://sayapp.company'
app.config['SQLALCHEMY_DATABASE_URI'] = conf['dbUrl']
app.config['SANDBOX'] = True
app.config['IDPAY_API_KEY'] = "83bdbfa4-04e6-4593-ba07-3e0652ae726d"
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["DEBUG"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DELIVER_TO_CHILD_DELAY"] = 4 * 60 * 60 # 4 hours
app.config.update({
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 30
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
    broker_url='pyamqp://',
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
    celery.conf.timezone = 'Asia/Tehran'
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

migrate = Migrate(app, db)

idpay = IDPay(app.config['IDPAY_API_KEY'], app.config['SANDBOX'])

api = Api(app)
# api_bp = Blueprint('api', __name__)
# api = Api(api_bp)

# this function converts an object to a python dictionary
def obj_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in columns(obj)}


def columns(obj, relationships=False, synonyms=True, composites=False,
                 hybrids=True):
    cls = obj.__class__

    mapper = inspect(cls)
    for k, c in mapper.all_orm_descriptors.items():

        if k == '__mapper__':
            continue

        if c.extension_type == ASSOCIATION_PROXY:
            continue

        if (not hybrids and c.extension_type == HYBRID_PROPERTY) \
                or (not relationships and k in mapper.relationships) \
                or (not synonyms and k in mapper.synonyms) \
                or (not composites and k in mapper.composites):
            continue

        yield getattr(cls, k)



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


def utf8_response(response: dict, is_deep=False):
    date_keys = ["createdAt", "lastLogin", "lastUpdate"]
    date_temp = []
    data_out, deep_out, out = "", "", ""
    response_temp = copy.deepcopy(response)

    if is_deep:
        for key2 in response_temp.keys():
            for key1 in response_temp[key2].keys():
                if key1 in date_keys or "Date" in key1:
                    date_temp.append(f', "{key1}": "{str(response[key2].pop(key1))}"')

            for temp in date_temp:
                data_out += temp

            data_out += "}"

            deep_temp = (
                str(eval(str(response[key2]).encode("utf-8")))
                .replace("'", '"')
                .replace("\\u200c", "‌")[:-1]
                + data_out
            )
            deep_out += f'"{key2}": {deep_temp}, '
            data_out = ""
            date_temp.clear()

        deep_out = "{" + deep_out[:-2] + "}"
        deep_out = deep_out.replace(': "None"', ": null")
        deep_out = deep_out.replace(": None", ": null")
        deep_out = deep_out.replace(': "False"', ": false")
        deep_out = deep_out.replace(": False", ": false")
        deep_out = deep_out.replace(': "True"', ": true")
        deep_out = deep_out.replace(": True", ": true")

        return deep_out

    else:
        for key in response_temp.keys():
            if key in date_keys or "Date" in key:
                date_temp.append(f', "{key}": "{str(response.pop(key))}"')

        for temp in date_temp:
            data_out += temp

        data_out += "}"
        # normalizer = Normalizer()

        out = (
            str(eval(str(response).encode("utf-8")))
            .replace("'", '"')
            .replace("\\u200c", "‌")[:-1]
            + data_out
        )
        out = out.replace(': "None"', ": null")
        out = out.replace(": None", ": null")
        out = out.replace(': "False"', ": false")
        out = out.replace(": False", ": false")
        out = out.replace(': "True"', ": true")
        out = out.replace(": True", ": true")

        return out


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    from ..models.revoked_token_model import RevokedTokenModel
    from sqlalchemy.orm import scoped_session, sessionmaker
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=db)
    )
    return RevokedTokenModel.is_jti_blacklisted(jti, session)

