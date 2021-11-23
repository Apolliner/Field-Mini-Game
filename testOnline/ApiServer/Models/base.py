from init import db
from sqlalchemy.ext.associationproxy import association_proxy

class Base(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)