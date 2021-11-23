"""
    Тестирование возможности реализации сервера многопользовательской игры через синхронный сервер, изменяющий
    игровой мир, записанный в БД SQLite, ApiServer на основе flask, позволяющее получать данные из БД и записывать в БД,
    а так же клиенты, работающие с ApiServer, выводящие картинку на экран и принимающие изображение экрана.

    Здесь реализуется сервер игры.
"""
import time
import random
from init import db
from Models.base import Base


def main_loop():
    item = Base.query.first()
    while True:
        if random.randrange(100)//50 > 0:
            item.count += 1
        else:
            item.count -= 1

        db.session.commit()
        time.sleep(0.1)

main_loop()