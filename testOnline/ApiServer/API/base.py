from flask_restful import Resource
from flask import request
from init import app, db
from Models.base import Base
from decorators import json_required
import random


class RBase(Resource):
    @json_required
    def get(self, **kwargs):
        base = Base.query.first()
        return base.count

    def post(self, **kwargs):
        count = random.randrange(999999)
        x = random.randrange(10)
        y = random.randrange(10)
        base = Base(count=count, x=x, y=y)
        db.session.add(base)
        db.session.commit()
        return {"count": count, "x": x, "y": y}

    @json_required
    def put(self, **kwargs):
        data = request.get_json(force=True)
        bases = Base.query.all()
        answer = {"other": list()}
        for base in bases:
            if base.count == data['count']:
                base.x = data['x']
                base.y = data['y']
                answer['owner'] = {"count": base.count, "x": base.x, "y": base.y}
            else:
                answer['other'].append({"count": base.count, "x": base.x, "y": base.y})
        db.session.commit()
        return answer
