from flask import jsonify, make_response

from say.orm import obj_to_dict


def json(f, *args, **kwargs):

    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)

        if isinstance(result, tuple):
            return make_response(*result)

        return jsonify(obj_to_dict(result))

    return wrapper
