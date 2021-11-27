from init import db
from sqlalchemy.ext.associationproxy import association_proxy


class Player(db.Model):
    id =                    db.Column(db.Integer, primary_key=True)
    unique =                db.Column(db.Integer, unique=True)
    name =                  db.Column(db.Integer)
    type =                  db.Column(db.String)
    icon =                  db.Column(db.String)
    x_dynamic =             db.Column(db.Integer)
    y_dynamic =             db.Column(db.Integer)
    x_world =               db.Column(db.Integer)
    y_world =               db.Column(db.Integer)
    chunk =                 db.Column(db.String)
    level =                 db.Column(db.Integer)
    vertices =              db.Column(db.Integer)
    assemblage_point_x =    db.Column(db.Integer)
    assemblage_point_y =    db.Column(db.Integer)
    direction =             db.Column(db.String)
