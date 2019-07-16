import os

from flask import Flask, jsonify, json, Response, request, Blueprint, send_from_directory
from flask_restful import Api, Resource
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from flasgger import Swagger
from flasgger.utils import swag_from
from werkzeug.utils import secure_filename

db = create_engine('postgresql://postgres:13771998@localhost:5432/say_db')

UPLOAD_FOLDER = "C:\\Users\\Parsa\\PycharmProjects\\SAY\\say\\files"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'wav', 'm4a', 'wma', 'mp3', 'aac', 'ogg'}

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Swagger(app)

api = Api(app)
# api_bp = Blueprint('api', __name__)
# api = Api(api_bp)

global otp_code


# this function converts an object to a python dictionary
def obj_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS