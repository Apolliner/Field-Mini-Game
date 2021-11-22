from os import path, mkdir
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


data_path = './files'

if not path.exists(data_path):
    mkdir(data_path)


def init_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    conn = 'sqlite:///./test.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = conn
    api = Api(app)
    return app, api


app, api = init_app()
db = SQLAlchemy(app)
migrate = Migrate(app, db)
