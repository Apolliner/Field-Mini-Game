from init import db
from sqlalchemy.ext.associationproxy import association_proxy


class PlayerRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=True, nullable=False)
    time = db.Column(db.Datetime)
    type = db.Column(db.String)
    description = db.Column(db.String)

"""
PlayerRequest
    id
    player_id
    time
    type
    description
"""