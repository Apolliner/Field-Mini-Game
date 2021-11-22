"""
    Тестирование возможности реализации сервера многопользовательской игры через синхронный сервер, изменяющий
    игровой мир, записанный в БД SQLite, ApiServer на основе flask, позволяющее получать данные из БД и записывать в БД,
    а так же клиенты, работающие с ApiServer, выводящие картинку на экран и принимающие изображение экрана.

    Здесь реализуется API игры, позволяющее посредством sqlite связывать клиент и сервер.
"""
from init import db, app, api
from routes import register_routes
from dicts import initialize_dictionaries

db.create_all()
register_routes(api)

if __name__ == '__main__':
    initialize_dictionaries(db)
    app.run(debug=True)
