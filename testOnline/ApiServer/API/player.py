import datetime
import json

from flask_restful import Resource
from flask import request
from init import app, db
from Models.player import Player
from Models.playerRequest import PlayerRequest
from decorators import json_required
import random


class RPlayerPost(Resource):

    def post(self, **kwargs):
        """ Создание нового игрока """
        unicue = random.randrange(9999999999)
        new_player_model = Player(unique=unicue)
        db.session.add(new_player_model)
        db.session.commit()
        player_model = Player.query.filter_by(unique=unicue).first()
        if player_model is not None:
            return {"message": "new player created", "player_id": player_model.id, "unique": player_model.unique}
        return {"message": "new player error created"}

class RPlayer(Resource):

    def get(self, player_id, **kwargs):
        """ Получение положения персонажа"""
        player_model = Player.query.filter_by(id=player_id).first()
        if player_model is None:
            return {"message": "player not found"}

        answer = {
            "icon": player_model.icon,
            "name": player_model.name,
            "type": player_model.type,
            "dynamic_position": [player_model.y_dynamic, player_model.x_dynamic],
            "world_position": [player_model.y_world, player_model.x_world],
            "chunks_use_map": player_model.chunk,
            "level": player_model.level,
            "vertices": player_model.vertices,
            "direction": player_model.direction
        }
        return answer

    def post(self, player_id, **kwargs):
        """ Отправка запроса """
        player_model = Player.query.filter_by(id=player_id).first()
        if player_model is None:
            return {"message": "player not found"}
        data = request.get_json(force=True)
        player_request = PlayerRequest.query.filter_by(player_id=player_id).first()
        if player_request is None:
            player_request = PlayerRequest(player_id=player_id, time=datetime.datetime.today(), type=data['type'],
                                           description=data['description'])
            db.session.add(player_request)
        else:
            player_request.date = datetime.datetime.today()
            player_request.type = data['type']
            player_request.description = data['description']

        db.session.commit()
        return {"message": "true"}
