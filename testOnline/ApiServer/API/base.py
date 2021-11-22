from flask_restful import Resource
from init import app, db


class RBase(Resource):
    def get(self, **kwargs):

        return "test"

