import os, shutil, copy

from flask import Flask, jsonify, json, Response, request, Blueprint, send_from_directory
from flask_restful import Api, Resource
from sqlalchemy import create_engine, inspect, or_, not_, and_
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from flasgger import Swagger
from flasgger.utils import swag_from
from werkzeug.utils import secure_filename
# from hazm import *
import json
from flask_cors import CORS


with open('./config.json') as config_file:
    conf = json.load(config_file)
# db = create_engine('postgresql://postgres:13771998@localhost:5432/postgres')
db = create_engine(conf['dbUrl'])
# db = create_engine('postgresql://postgres:postgres@5.253.27.219:5432/postgres')

BASE_FOLDER = os.getcwd()

UPLOAD_FOLDER = os.path.join(BASE_FOLDER, 'say')
UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'files')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

FLAGS = os.path.join(BASE_FOLDER, 'say')
FLAGS = os.path.join(FLAGS, 'flags')

ALLOWED_VOICE_EXTENSIONS = {'wav', 'm4a', 'wma', 'mp3', 'aac', 'ogg'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SWAGGER'] = {
    # "swagger_version": "3.20.9",
    "specs": [
        {
            "version": "2.0",
            "title": "SAY API",
            "endpoint": 'api_v2',
            "route": '/api/v2',
        }
    ]
}

Swagger(app)

api = Api(app)
# api_bp = Blueprint('api', __name__)
# api = Api(api_bp)


# this function converts an object to a python dictionary
def obj_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def allowed_voice(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VOICE_EXTENSIONS


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def utf8_response(response: dict, is_deep=False):
    date_keys = ['createdAt', 'lastLogin', 'lastUpdate']
    date_temp = []
    data_out, deep_out, out = '', '', ''
    response_temp = copy.deepcopy(response)

    if is_deep:
        for key2 in response_temp.keys():
            for key1 in response_temp[key2].keys():
                if key1 in date_keys or 'Date' in key1:
                    date_temp.append(f', "{key1}": "{str(response[key2].pop(key1))}"')

            for temp in date_temp:
                data_out += temp

            data_out += '}'

            deep_temp = str(eval(str(response[key2]).encode('utf-8'))).replace("'", '"').replace(
                '\\u200c', '‌')[:-1] + data_out
            deep_out += f'"{key2}": {deep_temp}, '
            data_out = ''
            date_temp.clear()

        deep_out = '{' + deep_out[:-2] + '}'
        deep_out = deep_out.replace(': "None"', ': null')
        deep_out = deep_out.replace(': None', ': null')
        deep_out = deep_out.replace(': "False"', ': false')
        deep_out = deep_out.replace(': False', ': false')
        deep_out = deep_out.replace(': "True"', ': true')
        deep_out = deep_out.replace(': True', ': true')

        return deep_out

    else:
        for key in response_temp.keys():
            if key in date_keys or 'Date' in key:
                date_temp.append(f', "{key}": "{str(response.pop(key))}"')

        for temp in date_temp:
            data_out += temp

        data_out += '}'
        # normalizer = Normalizer()

        out = str(eval(str(response).encode('utf-8'))).replace("'", '"').replace('\\u200c', '‌')[:-1] + data_out
        out = out.replace(': "None"', ': null')
        out = out.replace(': None', ': null')
        out = out.replace(': "False"', ': false')
        out = out.replace(': False', ': false')
        out = out.replace(': "True"', ': true')
        out = out.replace(': True', ': true')

        return out
