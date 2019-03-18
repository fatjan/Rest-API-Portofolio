import random, logging
from blueprints import db
from flask_restful import fields

class PopProducts(db.Model):
    __tablename__ = "pop_product"
    id = db.Column(db.Integer, primary_key=True) #product id diambil dari id table product.
    # product_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False) #nama product diambil dari table product melalui product_id
    penjual = db.Column(db.String(255), nullable=False) #nama penjual diambil dari table product melalui product_id
    terjual = db.Column(db.Integer, nullable=False) #minimum untuk jadi popular product adalah ketika terbeli sudah mencapai 25
    
    response_field = {
        'id' : fields.Integer,
        'name' : fields.String,
        'penjual' : fields.String,
        'terjual' : fields.String,
    }

    def __init__(self, id, name, penjual, terjual):
        self.id = id
        self.name = name
        self.penjual = penjual
        self.terjual = terjual
        
    def __repr__(self): #initiate table model
        return '<Pop_Product %r>' % self.id #the __repr__ must have a string type as return
  