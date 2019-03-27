import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from . import *
from ..product import *
from ..pop_product import *
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims
import datetime

bp_cart = Blueprint('cart', __name__)
api = Api(bp_cart)

class CartResource(Resource): 

    def __init__(self):
        pass
    
    @jwt_required  #for pembeli to see their carts
    #for penjual to send their products once the status is paid
    def get(self, id=None):
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location='args', default=1)
            parser.add_argument('rp', type=int, location='args', default=5)
            parser.add_argument('user_id', location='args')
            parser.add_argument('pembeli', location='args')
            parser.add_argument('item', location='args')
            parser.add_argument('product_id', location='args')
            parser.add_argument('jumlah', location='args')
            parser.add_argument('status', location='args')
            args = parser.parse_args()
            rumus_offset = args['p'] * args['rp'] - args['rp']
            qry = Carts.query

            #if token belongs to pembeli
            if get_jwt_claims()['user_type'] == 'publik':
                qry = qry.filter_by(pembeli=get_jwt_claims()['name'])
            
            #if token belongs to admin
            if args['item'] is not None:
                qry = qry.filter(Carts.item.like("%"+args['item']+"%")) #for name with this name, and not case sensitive
            if args['product_id'] is not None:
                qry = qry.filter_by(product_id=args['product_id'])
            if args['status'] is not None:
                qry = qry.filter_by(status=args['status']) #qry that is filtered by name >> for exact name
            

            #if token belongs to penjual
            # if get_jwt_claims()['user_type'] == 'penjual':
            #     baris = []
            #     for i in qry.all():
            #         penjual = get_jwt_claims()['name']
            #         product_id = i.product_id
            #         qry_product = Products.query.get(product_id)
            #         if qry_product.penjual == penjual and i.status=='paid':
            #             baris.append(marshal(i, Carts.response_field))    
            #     return {"code": "200", "status": "OK", "message":"cart is on display", "data": baris}, 200, {'Content-Type': 'application/json'}

            rows = []
            for row in qry.limit(args['rp']).offset(rumus_offset).all():        
                rows.append(marshal(row, Carts.response_field))
            # if get_jwt_claims()['id'] == 'user_id':
            return {"code": 200, "message": "OK", "data":rows}, 200, {'Content-Type': 'application/json'}
            # return {'message': 'Sorry, this page is not accessible'}, 404, {'Content-Type': 'application/json'}
        else:
            qry = Carts.query.get(id) #select * from where id = id
            if qry != None and id == get_jwt_claims()['id']:
                return {"code": 200, "message": "OK", "data":marshal(qry, Carts.response_field)}, 200, {'Content-Type': 'application/json'}   
            return {'status': 'not found', 'message': 'you can only see your profile details'}, 404, {'Content-Type': 'application/json'}
            #publik (pembeli) can only see their own cart
        
    @jwt_required
    def post(self): #for everyone to register and login        
        parser = reqparse.RequestParser()
        pembeli = get_jwt_claims()['name']
        parser.add_argument('product_id', location='json')
        args = parser.parse_args() #this becomes str_serialized
        qry_product = Products.query.get(args['product_id'])
        item = qry_product.name
        harga = qry_product.harga #harga satuan barang dari table product.
        parser.add_argument('jumlah', location='json')
        parser.add_argument('detail', location='json')
        # parser.add_argument('status', location='json')
        args = parser.parse_args() #this becomes str_serialized
        created_at = datetime.datetime.now().strftime("%c")
        updated_at = datetime.datetime.now().strftime("%c")
        status = 'paid'
        if qry_product.kota == get_jwt_claims()['kota']: #kalau kota pembeli dan penjual sama, ongkir = 9000 per item, kalau beda, ongkir = 15000 per item
            ongkir = 9000 * int(args['jumlah'])
        else:
            ongkir = 15000 * int(args['jumlah'])
        total_harga = harga * int(args['jumlah']) + ongkir #total harga = harga satuan barang * jumlah barang + ongkos kirim (ongkir)
        address = get_jwt_claims()['address']
        kota = get_jwt_claims()['kota']
        #masukin created_at and updated_at di table n di cart_new
        cart_new = Carts(None, pembeli, item, harga, args['product_id'], args['jumlah'], args['detail'] , ongkir, total_harga, 'not yet paid', address, kota)
        db.session.add(cart_new) #insert the input data into the database
        db.session.commit() 
        if cart_new.status == 'paid':
            qry_product.tersedia -= int(args['jumlah'])
            # kalau barang sudah dibeli oleh pembeli, jumlah barang tersedia yang ada di table product akan berkurang pada product yang dibeli tersebut.
            db.session.commit()
            #kemudian data di pop_product akan bertambah.
            qry_pop_product = PopProducts.query.get(qry_product.id)
            if qry_pop_product is None: 
                terjual = int(args['jumlah'])
                pop_product_new = PopProducts(qry_product.id, qry_product.name, qry_product.penjual, terjual, qry_product.urlimage)
                db.session.add (pop_product_new)
                db.session.commit()
            else: 
                qry_pop_product.terjual += int(args['jumlah'])
                db.session.commit()
        # return marshal(cart_new, Carts.response_field), 200, {'Content-Type': 'application/json'}  
        return {"code": 200, "message": "OK", "data": marshal(cart_new, Carts.response_field)}, 200, {'Content-Type': 'application/json'} 
    
    @jwt_required #if pembeli wants to change their cart details, e.g.: the cart status was previously "not yet paid"
    #and then changed to "paid", then the transaction becomes successful and the amount of bought items will be included in the pop_products jumlah terbeli.
    def put(self, id):
        parser = reqparse.RequestParser()
        #pembeli tidak bisa mengganti product_id yang ingin dibeli.
        #ketika ingin cancel pembelian, harus delete cart kemudian post cart baru untuk membeli.
        #maka dari itu, cart hanya bisa di edit untuk jumlah, detail atau status nya saja.
        #dan edit cart ini hanya bisa dilakukan ketika status cart nya 'not yet paid'. Kalau sudah 'paid', cart tidak bisa diedit.
        parser.add_argument('jumlah', location='json')
        parser.add_argument('detail', location='json')
        parser.add_argument('status', location='json')
        args = parser.parse_args()
        qry_cart = Carts.query.get(id)
        pembeli = qry_cart.pembeli
        status_before_edit = qry_cart.status
        if qry_cart is not None and get_jwt_claims()['name'] == pembeli and status_before_edit != "paid":
            #user_type publik adalah pembeli yang sudah register, jadi bisa membeli barang.
            if args['jumlah'] is not None: #ketika pembeli merubah jumlah barang yang dipesan, otomatis harga ongkir dan total harga juga akan berubah.
                qry_cart.jumlah = args['jumlah']
                qry_product = Products.query.get(qry_cart.product_id)
                harga = qry_product.harga #harga satuan barang dari table product.
                if qry_product.kota == get_jwt_claims()['kota']: #kalau kota pembeli dan penjual sama, ongkir = 9000 per item, kalau beda, ongkir = 15000 per item
                    ongkir = 9000 * int(args['jumlah'])
                else:
                    ongkir = 15000 * int(args['jumlah'])
                qry_cart.ongkir = ongkir
                qry_cart.total_harga = harga * int(args['jumlah']) + ongkir
            if args['detail'] is not None:
                qry_cart.detail = args['detail']
            if args['status'] is not None:
                qry_cart.status = args['status']
            db.session.commit()
            if qry_cart.status == 'paid': #if previously it was not paid and then changed to paid.
                #product tersedia berkurang sesuai jumlah, pop product terbeli bertambah sesuai jumlah.
                qry_pop_product = PopProducts.query.get(qry_cart.product_id)
                qry_product = Products.query.get(qry_cart.product_id)
                if qry_pop_product is None: 
                    terjual = qry_cart.jumlah
                    pop_product_new = PopProducts(qry_product.id, qry_product.name, qry_product.penjual, terjual, qry_product.urlimage)
                    db.session.add (pop_product_new)
                    db.session.commit()
                else: 
                    qry_pop_product.terjual += qry_cart.jumlah
                    db.session.commit()
                qry_product.tersedia -= qry_cart.jumlah
                db.session.commit()

            return {"code": "200", "status": "OK", "message":"your cart has been edited", "cart": marshal(qry_cart, Carts.response_field)}, 200, {'Content-Type': 'application/json'}
        elif get_jwt_claims()['name'] != pembeli:
            return {"code": "404", "status": "bad request", "message":'Anuthorized. Cannot edit this cart.'}, 404, {'Content-Type': 'application/json'}
        elif status_before_edit == "paid": 
            return {"code": "404", "status": "bad request", "message":'Cart with id number = %d is already paid and cannot be edited' % id}, 404, {'Content-Type': 'application/json'}
        return {"code": "404", "status": "bad request", "message":'Cart with that id number is not found'}, 404, {'Content-Type': 'application/json'}

        


    @jwt_required #delete user is only for admin if any users do some violation of use.  
    #or if the user itself wants to delete profile due to their own willingness to delete their profile.
    def delete(self, id):
        qry_del = Carts.query.get(id)
        if qry_del is not None: 
            qry_cart = Carts.query.get(id) 
            pembeli = qry_cart.pembeli
            if get_jwt_claims()['name'] == pembeli:
                db.session.delete(qry_del)
                db.session.commit()
                return {"code": "200", "status": "OK", "message":'Cart with id = %d has been deleted' % id}, 200, {'Content-Type': 'application/json'}
        return {"code": "404", "status": "bad request", "message": 'ID_IS_NOT_FOUND'}, 404, {'Content-Type': 'application/json'}
        
    def patch(self):
        return 'Not yet implemented', 501

api.add_resource(CartResource, '', '/<int:id>')
