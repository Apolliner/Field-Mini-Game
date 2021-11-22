from testOnline.ApiServer.init import db
from sqlalchemy.ext.associationproxy import association_proxy

class Base(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)