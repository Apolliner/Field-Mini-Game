from flask import request
from flask_restful import abort

def json_required(method):
    def wrapper(*args, **kwargs):
        if request.get_json(force=True) is None:
            abort(400, message='no input data')
        return method(*args, **kwargs)

    return wrapper