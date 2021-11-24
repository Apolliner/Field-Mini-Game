from init import db
from sqlalchemy.ext.associationproxy import association_proxy


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x_dynamic = db.Column(db.Integer)
    y_dynamic = db.Column(db.Integer)
    x_global = db.Column(db.Integer)
    y_global = db.Column(db.Integer)
    x_local = db.Column(db.Integer)
    y_local = db.Column(db.Integer)
    chunk = db.Column(db.String)


"""
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
"""