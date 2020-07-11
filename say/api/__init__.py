import os

from flask import (
    Flask,
)
from flask_restful import Api
from flasgger import Swagger
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from logging import basicConfig, DEBUG
from flask_caching import Cache
from flask_cors import CORS
import flask_monitoringdashboard as dashboard
from mailerlite import MailerLiteApi

from say.config import config
from say.payment import IDPay
from say.celery import create_celery_app
from say.sms import MeliPayamak

PRODUCTION = os.environ.get('PRODUCTION')
DEFAULT_CHILD_ID = 104  # TODO: Remove this after implementing pre needs

CELERY_TASK_LIST = [
    'say.tasks',
]

basicConfig(level=DEBUG)

UPLOAD_FOLDER = "files"
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config.update(config)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
celery = create_celery_app(app)
cache = Cache(app)
swagger = Swagger(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
)
mail = Mail(app)
jwt = JWTManager(app)
idpay = IDPay(app.config['IDPAY_API_KEY'], app.config['SANDBOX'])
sms_provider = MeliPayamak(
    app.config['MELI_PAYAMAK_USERNAME'],
    app.config['MELI_PAYAMAK_PASSWORD'],
    app.config['MELI_PAYAMAK_FROM'],
)
mailerlite = MailerLiteApi(app.config.get('MAILERLITE_API_KEY', 'not-entered'))


@app.before_first_request
def insert_basedata():
    try:
        from say.basedata import basedata
        basedata()
    except:
        pass


APIMD_CONFIG_FILE_PROD = 'apimd-config-prod.cfg'
APIMD_CONFIG_FILE = 'apimd-config.cfg'
if PRODUCTION:
    if not os.path.isfile(APIMD_CONFIG_FILE_PROD):
        raise Exception('''
            Make sure apimd-config-prod.cfg exist
            and admin PASSWORD, CUSTOM_LINK, SECURITY_TOKEN and DATABASE
            are correctly set in apimd-config-prod.cfg
        ''')

    dashboard.config.init_from(file=APIMD_CONFIG_FILE_PROD)
# else:
#     dashboard.config.init_from(file=APIMD_CONFIG_FILE)
#     print(
#         'Open http://localhost/dashboard and use admin admin to see '
#         'API monitoring dashboard'
#     )
#
# try:
#     dashboard.bind(app)
# except Exception as e:
#     print('''
#         Make sure apimd-config-prod.cfg exist
#         and admin PASSWORD, CUSTOM_LINK, SECURITY_TOKEN and DATABASE
#         are correctly set in apimd-config-prod.cfg
#         '''
#     )
#     raise

api = Api(app)


