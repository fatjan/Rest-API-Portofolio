import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from . import *
from ..product import *
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims
import random

bp_pop_product = Blueprint('pop_product', __name__)
api = Api(bp_pop_product)

class PopProductResource(Resource): 

    def __init__(self):
        pass
    
    #accessible by all users, even those who are not registered user. No token required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=7)
        # parser.add_argument('kategori', location='args')
        # parser.add_argument('type', location='args')
        parser.add_argument('name', location='args')
        # parser.add_argument('harga', location='args')
        # parser.add_argument('brand', location='args')
        # parser.add_argument('tersedia', location='args')
        # parser.add_argument('kota', location='args')
        parser.add_argument('penjual', location='args')
        args = parser.parse_args()
        rumus_offset = args['p'] * args['rp'] - args['rp']
        qry = PopProducts.query
        # if args['kategori'] is not None:
        #     qry = qry.filter(Products.kategori.like("%"+args['kategori']+"%")) 
        # if args['type'] is not None:
        #     qry = qry.filter_by(Products.type.like("%"+args['type']+"%")) 
        if args['name'] is not None:
            qry = qry.filter(PopProducts.name.like("%"+args['name']+"%"))    
        # if args['harga'] is not None:
        #     qry = qry.filter(Products.harga.like("%"+args['harga']+"%"))    
        # if args['brand'] is not None:
        #     qry = qry.filter(Products.brand.like("%"+args['brand']+"%"))
        # if args['kota'] is not None:
        #     qry = qry.filter(Products.kota.like("%"+args['kota']+"%")) 
        if args['penjual'] is not None:
            qry = qry.filter(PopProducts.penjual.like("%"+args['penjual']+"%")) 
        # if args['tersedia'] is not None:
        #     qry = qry.filter_by(tersedia=args['tersedia']) 
        rows = []
        for row in qry.limit(args['rp']).offset(rumus_offset).all():
            if row.terjual >= 10:
                rows.append(marshal(row, PopProducts.response_field))
        if rows is not []:
            return {"code": "200", "status": "OK", "message":"popular products are on display", "pop_products": rows}, 200, {'Content-Type': 'application/json'}
        return {"code": "404", "status": "bad request", "message": 'Barang yang anda cari tidak dapat ditemukan'}, 404, {'Content-Type': 'application/json'}
        # else:
        #     qry = Products.query.get(id) #select * from where id = id
        #     if qry != None:
        #         return marshal(qry, Products.response_field), 200, {'Content-Type': 'application/json'}   
        #     return {'status': 'not found', 'message': f'Product dengan id: {id} tidak ditemukan'}, 404, {'Content-Type': 'application/json'}
        
    def patch(self):
        return 'Not yet implemented', 501

api.add_resource(PopProductResource, '')

class PopProductAdminResource(Resource): 

    def __init__(self):
        pass
    
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=7)
        args = parser.parse_args()
        rumus_offset = args['p'] * args['rp'] - args['rp']
        qry = PopProducts.query
        rows = []
        #if admin wants to see all bought products
        if get_jwt_claims()['user_type'] == 'admin':
            for row in qry.limit(args['rp']).offset(rumus_offset).all():
                    rows.append(marshal(row, PopProducts.response_field))
            if rows is not []:
                return rows, 200, {'Content-Type': 'application/json'}
            return {'message': 'Barang yang anda cari tidak dapat ditemukan'}, 404, {'Content-Type': 'application/json'}

        #if penjual wants to see their bought products
        if get_jwt_claims()['user_type'] == 'penjual':
            baris = []
            for i in qry.all():
                penjual = get_jwt_claims()['name']
                qry_product = Products.query.get(i.id)
                if qry_product.penjual == penjual:
                    baris.append(marshal(i, PopProducts.response_field))    
            return baris, 200, {'Content-Type': 'application/json'}


        if get_jwt_claims()['user_type'] == 'penjual':
            for row in qry.limit(args['rp']).offset(rumus_offset).all():
                    rows.append(marshal(row, PopProducts.response_field))
            if rows is not []:
                return rows, 200, {'Content-Type': 'application/json'}
            return {'message': 'Barang yang anda cari tidak dapat ditemukan'}, 404, {'Content-Type': 'application/json'}



    @jwt_required #admin can delete popular products if required.  
    def delete(self, id):
        qry_del = PopProducts.query.get(id)
        del_pop_product = marshal(qry_del, PopProducts.response_field)
        if qry_del is not None and get_jwt_claims()['user_type'] == 'admin':
            db.session.delete(qry_del)
            db.session.commit()
            return {"code": "200", "status": "OK", "message":'Popular product with id = %d has been deleted' % id, "deleted popular product": del_pop_product}, 200, {'Content-Type': 'application/json'}
        return {"code": "404", "status": "bad request", "message": 'ID_IS_NOT_FOUND'}, 404, {'Content-Type': 'application/json'}

api.add_resource(PopProductAdminResource, '/admin', '/admin/<int:id>')
        