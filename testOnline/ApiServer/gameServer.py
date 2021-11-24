"""
    Тестирование возможности реализации сервера многопользовательской игры через синхронный сервер, изменяющий
    игровой мир, записанный в БД SQLite, ApiServer на основе flask, позволяющее получать данные из БД и записывать в БД,
    а так же клиенты, работающие с ApiServer, выводящие картинку на экран и принимающие изображение экрана.

    Здесь реализуется сервер игры.
"""
import copy
import time
import random
from init import db
from Models.base import Base



def main_loop():
    """

    СТРУКТУРА GAME_LOOP:
        загрузка игровой карты
        набирает пулл игроков
        запускает цикл
            запрашивает пулл игроков
            проходит циклом по пулу игроков.
                Получает запрос пользователя и удаляет его
                обрабатывает запрос пользователя
                записывает в БД результат рассчётов

    ИСПОЛЬЗУЕМЫЕ МОДЕЛИ:
        Player
            id
            x_dynamic
            y_dynamic
            x_global
            y_global
            x_local
            y_local
            chunk
            requests    ?

        PlayerRequest
            id
            player_id
            time
            type
            description

    """
    step = 0
    item = Base.query.first()
    while True:
        players = Player.query.all()
        for player in players:
            player_requests = PlayerRequest.query.order_by(time.desc()).all()
            player_request = copy.deepcopy(player_requests[0])
            player = []





        db.session.commit()
        step += 1

main_loop()