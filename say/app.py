import os
import re
from logging import basicConfig

import psycopg2
import sqlalchemy
from flasgger import Swagger
from flask import Flask
from flask import jsonify
from flask_cors import CORS
from pydantic.error_wrappers import ValidationError

from say.api.ext import api
from say.api.ext import cache
from say.api.ext import jwt
from say.api.ext import limiter
from say.api.ext import mail
from say.api.ext import setup_healthz
from say.config import configs
from say.exceptions import HTTPException
from say.orm import create_engine
from say.orm import init_model
from say.orm import session
from say.sentry import setup_sentry


basicConfig(level=configs.LOGLEVEL)

BASE_FOLDER = os.getcwd()

if not os.path.isdir(configs.UPLOAD_FOLDER):
    os.makedirs(configs.UPLOAD_FOLDER)

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


Swagger(app)

cache.init_app(app)
jwt.init_app(app)
mail.init_app(app)
api.init_app(app)
limiter.init_app(app)
setup_healthz(app)
setup_sentry()


@app.before_first_request
def setup_i18n():
    from say.i18n import setup

    setup()


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(ValidationError)
def handle_pydantic_validation_errors(e):
    return jsonify(e.errors()), 400


DUPPLICATE_ENTRY_PATTERN = re.compile(r'Key \((.*)\)=\((.*)\)')


@app.errorhandler(sqlalchemy.exc.IntegrityError)
def handle_sqlalchemy_integrity_error(e):
    if isinstance(e.orig, psycopg2.errors.UniqueViolation):
        entry = DUPPLICATE_ENTRY_PATTERN.search(e.orig.pgerror)
        if not entry:
            raise e

        return jsonify(message=f'Duplicate key: {entry.group(1)}={entry.group(2)}'), 400

    raise e


@app.before_first_request
def init_orm():
    engine = session.bind or create_engine(url=configs.postgres_url)
    init_model(engine)


@app.before_first_request
def create_data_dir():
    if not os.path.isdir(configs.UPLOAD_FOLDER):
        os.makedirs(configs.UPLOAD_FOLDER)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    session.remove()
    return response_or_exc
