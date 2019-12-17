from flask import make_response, jsonify


HTTP_PERMISION_DENIED = lambda: make_response(jsonify(message='Permission Denied'), 403)
HTTP_NOT_FOUND = lambda: make_response(jsonify(message='Not Found'), 404)

