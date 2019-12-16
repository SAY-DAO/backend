from flask import make_response, jsonify


HTTP_PERMISION_DENIED = lambda: make_response(jsonify(message='Permission Denied'), 403)

