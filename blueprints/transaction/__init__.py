import random, logging
from blueprints import db
from flask_restful import fields

class Transactions(db.Model):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pembeli = db.Column(db.String(255), nullable=False) #nama pembeli diambil dari token
    item = db.Column(db.String(255), nullable=True) #nama barang yang dibeli
    harga = db.Column(db.Integer, nullable=False) #harga satuan.
    product_id = db.Column(db.Integer) #product id dari id di table product
    jumlah = db.Column(db.String(255), nullable=False, unique=True)
    total_harga = db.Column(db.Integer)
    ongkir = db.Column(db.String(255), nullable=False) #dihitung dari jarak kota penjual ke pembeli. menggunakan kode pos?
    total = db.Column(db.Integer) #total harga + ongkir
    
    response_field = {
        'id' : fields.Integer,
        'pembeli' : fields.String,
        'item' : fields.String,
        'harga' : fields.Integer,
        'product_id' : fields.String,
        'jumlah' : fields.String,
        'detail' : fields.String,
        'ongkir' : fields.String,
        'address' : fields.String,
        'kota' : fields.String,
    }

    def __init__(self, id, pembeli, item, harga, product_id, jumlah, detail, ongkir, address, kota):
        self.id = id
        self.pembeli = pembeli
        self.item = item
        self.harga = harga
        self.product_id = product_id
        self.jumlah = jumlah
        self.detail = detail
        self.ongkir = ongkir
        self.address = address
        self.kota = kota
       
    def __repr__(self): #initiate table model
        return '<Cart %r>' % self.id #the __repr__ must have a string type as return
  