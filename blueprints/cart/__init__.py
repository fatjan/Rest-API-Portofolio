import random, logging
from blueprints import db
from flask_restful import fields

class Carts(db.Model):
    __tablename__ = "cart"
    #untuk membeli sebuah product, pembeli tinggal masuk ke endpoint cart dan memasukkan 'post' nomor id product
    #masukkan id barang yang ingin dibeli, jumlah barang yang ingin dibeli dan detail keterangan pesanan, status pemesanan: paid or belum.
    #data lainnya diambil dari table product, atau dari token untuk data tentang user.
    #ongkir di setting di code resources cart.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pembeli = db.Column(db.String(255), nullable=False) #nama pembeli diambil dari token
    item = db.Column(db.String(255), nullable=True) #nama barang yang dibeli, dari table product
    harga = db.Column(db.Integer, nullable=False) #harga barang yang dibeli, dari table product
    product_id = db.Column(db.Integer) #product id dari id di table product
    jumlah = db.Column(db.Integer)
    detail = db.Column(db.String(255), nullable=False, unique=True) #untuk pembeli memberikan keterangan tentang
    #barang yang dipesannya. misal warna coklat, ukuran M.
    ongkir = db.Column(db.Integer) #dihitung dari jarak kota penjual ke pembeli. menggunakan kode pos?
    total_harga = db.Column(db.Integer, nullable=False) #total harga ditambah ongkos kirim.
    status = db.Column(db.String(255), nullable=False) #apakah barang sudah dibayar apa belum.
    #kalau status sudah paid, required detail akan dimasukkan ke table transaction.
    address = db.Column(db.String(255), nullable=False) #diambil dari token karena user memiliki data address.
    kota = db.Column(db.String(255), nullable=False) #untuk keperluan estimasi biaya pengiriman barang, juga diambil dari token.
    
    response_field = {
        'id' : fields.Integer,
        'pembeli' : fields.String,
        'item' : fields.String,
        'harga' : fields.Integer,
        'product_id' : fields.Integer,
        'jumlah' : fields.Integer,
        'detail' : fields.String,
        'ongkir' : fields.Integer,
        'total_harga' : fields.Integer,
        'status' : fields.String, #paid or belum
        'address' : fields.String, #alamat pembeli
        'kota' : fields.String, #kota tempat tinggal pembeli, untuk estimasi ongkir
    }

    def __init__(self, id, pembeli, item, harga, product_id, jumlah, detail, ongkir, total_harga, status, address, kota):
        self.id = id
        self.pembeli = pembeli
        self.item = item
        self.harga = harga
        self.product_id = product_id
        self.jumlah = jumlah
        self.detail = detail
        self.ongkir = ongkir
        self.total_harga = total_harga
        self.status = status
        self.address = address
        self.kota = kota
       
    def __repr__(self): #initiate table model
        return '<Cart %r>' % self.id #the __repr__ must have a string type as return
     