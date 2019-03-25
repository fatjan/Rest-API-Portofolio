import random, logging
from blueprints import db
from flask_restful import fields


class Products(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kategori = db.Column(db.String(255), nullable=False) #kategori product, contoh: men, women, accessories
    type = db.Column(db.String(255), nullable=False) #tipe product, contoh: sepatu, baju, celana
    name = db.Column(db.String(255), nullable=False) #nama product, contoh: kerudung pasmina
    harga = db.Column(db.Integer, nullable=False) #harga barang per item
    no_seri = db.Column(db.Integer, nullable=False) #no seri product, no need to key in, just take random 5 digit numbers
    brand = db.Column(db.String(255), nullable=False) #contoh: mango, zarra, nissa, gatsby
    detail = db.Column(db.String(255), nullable=False) #contoh: dibuat dengan bahan berkualitas, dll.
    penjual = db.Column(db.String(255), nullable=False) #nama penjual diambil dari token.
    #supaya penjual hanya boleh meng edit dan/atau menghapus products yang mereka jual saja, bukan dari penjual lain.
    tersedia = db.Column(db.Integer, nullable=False) #supaya pembeli tahu ada berapa banyak item yang tersedia dan juga
    #jumlah nya akan terkurangi ketika ada user_type = pembeli yang membeli product ini.
    kota = db.Column(db.String(255), nullable=False) #untuk pembeli memperkirakan ongkir. supaya tahu barang dikirim dari mana.
    urlimage = db.Column(db.String(255), nullable=False) #foto barang

    response_field = {
        'id' : fields.Integer,
        'kategori' : fields.String,
        'type' : fields.String,
        'name' : fields.String,
        'harga' : fields.Integer,
        'no_seri' : fields.Integer,
        'brand' : fields.String,
        'detail' : fields.String,
        'penjual' : fields.String,
        'tersedia' : fields.Integer,
        'kota' : fields.String,
        'urlimage' : fields.String
    }

    def __init__(self, id, kategori, type, name, harga, no_seri, brand, detail, penjual, tersedia, kota, urlimage):
        self.id = id
        self.kategori = kategori
        self.type = type
        self.name = name
        self.harga = harga
        self.no_seri = no_seri
        self.brand = brand
        self.detail = detail
        self.penjual = penjual
        self.tersedia = tersedia
        self.kota = kota
        self.urlimage = urlimage
       
    def __repr__(self): #initiate table model
        return '<Product %r>' % self.id #the __repr__ must have a string type as return
  