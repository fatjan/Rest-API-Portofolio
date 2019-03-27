import random, logging
from blueprints import db
from flask_restful import fields


class Users(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False, unique=True) #to be put on display
    #e.g. : user_type = penjual, nama penjual ditampilkan di product yang dijual
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    kota = db.Column(db.String(255), nullable=False) #untuk keperluan estimasi biaya pengiriman barang.
       
    response_field = {
        'id' : fields.Integer,
        'user_type' : fields.String,
        'username' : fields.String,
        'name' : fields.String,
        'password' : fields.String,
        'address' : fields.String,
        'kota' : fields.String,
    }
  
    def __init__(self, id, user_type, username, name, password, address, kota):
        self.id = id
        self.user_type = user_type
        self.username = username
        self.name = name
        self.password = password
        self.address = address
        self.kota = kota
       
    def __repr__(self): #initiate table model
        return '<User %r>' % self.id #the __repr__ must have a string type as return
  