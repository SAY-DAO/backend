import os
from logging import basicConfig, DEBUG

import flask_monitoringdashboard as dashboard
from flask import (
    Flask,
)

from say.api.resources import api, limiter
from say.celery import create_celery_app
from say.config import config
from .api.ext import jwt, mail, swagger, cache, cors
from .orm import create_engine, bind_session, session

PRODUCTION = os.environ.get('PRODUCTION')

basicConfig(level=DEBUG)


app = Flask(__name__)
app.config.update(config)

cors.init_app(app)
celery = create_celery_app(app)
cache.init_app(app)
swagger.init_app(app)
mail.init_app(app)
api.init_app(app)
limiter.init_app(app)
jwt.init_app(app)


def setup_monitoring(app):
    if not config['TESTING']:

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


@app.before_first_request
def init_orm():
    engine = session.bind or create_engine(url=config['dbUrl'])
    bind_session(engine)


@app.before_first_request
def create_data_dir():
    if not os.path.isdir(config['UPLOAD_FOLDER']):
        os.makedirs(config['UPLOAD_FOLDER'])


@app.teardown_request
def remove_session(ex):
    session.remove()


@app.teardown_appcontext
def dispose_engine(ex):
    session.bind.dispose()
