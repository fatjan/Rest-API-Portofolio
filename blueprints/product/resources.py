import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from . import *
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims
import random

bp_product = Blueprint('product', __name__)
api = Api(bp_product)

class ProductResource(Resource): 

    def __init__(self):
        pass
    
    #accessible by all users, even those who are not registered users. No token required
    def get(self, id=None):
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location='args', default=1)
            parser.add_argument('rp', type=int, location='args', default=7)
            parser.add_argument('kategori', location='args')
            parser.add_argument('type', location='args')
            parser.add_argument('name', location='args')
            parser.add_argument('max_harga', location='args')
            parser.add_argument('brand', location='args')
            parser.add_argument('tersedia', location='args')
            parser.add_argument('penjual', location='args')
            parser.add_argument('kota', location='args')
            parser.add_argument('search', location='args')
            
            args = parser.parse_args()
            rumus_offset = args['p'] * args['rp'] - args['rp']
            qry = Products.query
            if args['kategori'] is not None:
                qry = qry.filter_by(kategori=args['kategori']) 
            if args['type'] is not None:
                qry = qry.filter(Products.type.like("%"+args['type']+"%")) 
            if args['name'] is not None:
                qry = qry.filter(Products.name.like("%"+args['name']+"%"))    
            if args['brand'] is not None:
                qry = qry.filter(Products.brand.like("%"+args['brand']+"%"))
            if args['kota'] is not None:
                qry = qry.filter(Products.kota.like("%"+args['kota']+"%")) 
            if args['tersedia'] is not None:
                qry = qry.filter_by(tersedia=args['tersedia']) 
            if args['penjual'] is not None:
                qry = qry.filter(Products.penjual.like("%"+args['penjual']+"%"))  

            if  args['search'] is not None:
                qry = qry.filter_by(kategori=args['search']) 
                if qry.first() is None:
                    qry = Products.query.filter(Products.type.like("%"+args['search']+"%")) 
                    if qry.first() is None:
                        qry = Products.query.filter(Products.name.like("%"+args['search']+"%"))   
                        if qry.first() is None:
                            qry = Products.query.filter(Products.brand.like("%"+args['search']+"%"))
                            if qry.first() is None:
                                qry = Products.query.filter(Products.kota.like("%"+args['search']+"%"))
                                if qry.first() is None:
                                    return {'message': 'Barang yang anda cari tidak dapat ditemukan'}, 404, {'Content-Type': 'application/json'}

            rows = []
            for row in qry.limit(args['rp']).offset(rumus_offset).all():
                if args['max_harga'] is not None and row.harga <= int(args['max_harga']):
                    rows.append(marshal(row, Products.response_field))
                elif args['max_harga'] is None:
                    rows.append(marshal(row, Products.response_field))
            if rows is not []:
                return rows, 200, {'Content-Type': 'application/json'}
            return {'message': 'Barang yang anda cari tidak dapat ditemukan'}, 404, {'Content-Type': 'application/json'}
        else:
            qry = Products.query.get(id) #select * from where id = id
            if qry != None:
                return marshal(qry, Products.response_field), 200, {'Content-Type': 'application/json'}   
            return {'status': 'not found', 'message': f'Product dengan id: {id} tidak ditemukan'}, 404, {'Content-Type': 'application/json'}
    
    @jwt_required #only admin and seller who can post a product.
    def post(self): #for the seller to post their products 
        parser = reqparse.RequestParser()
        parser.add_argument('kategori', location='json')
        parser.add_argument('type', location='json')
        parser.add_argument('name', location='json')
        parser.add_argument('harga', location='json')
        no_seri = random.randrange (9999,99999,1)
        parser.add_argument('brand', location='json')
        parser.add_argument('detail', location='json')
        penjual = get_jwt_claims()['name']
        parser.add_argument('tersedia', location='json')
        kota = get_jwt_claims()['kota']
        args = parser.parse_args() #this becomes str_serialized
        if get_jwt_claims()['user_type'] == 'admin' or get_jwt_claims()['user_type'] == 'penjual':
            product_new = Products(None, args['kategori'], args['type'], args['name'], args['harga'], no_seri, args['brand'], args['detail'], penjual, args['tersedia'], kota)
            db.session.add(product_new) #insert the input data into the database
            db.session.commit() 
            return marshal(product_new, Products.response_field), 200, {'Content-Type': 'application/json'}
        return 'Failed to post a product, this page is not accessible.', 404, {'Content-Type': 'application/json'}

    # if admin wants to edit product whenever required.
    @jwt_required 
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('kategori', location='json')
        parser.add_argument('type', location='json')
        parser.add_argument('name', location='json')
        parser.add_argument('harga', location='json')
        parser.add_argument('brand', location='json')
        parser.add_argument('detail', location='json')
        parser.add_argument('tersedia', location='json')
        args = parser.parse_args()
        qry_product = Products.query.get(id)
        #id is found and the user type is penjual or admin, put can be used. publik cannot edit product data.
        #penjual can only edit their own selling products. cannot edit other seller's products.
        if qry_product is not None and get_jwt_claims()['user_type'] == 'admin':
            # penjual or admin can edit certain type of input only, if required. E.g. : only editing the detail of products, other requirements no need to be filled.
            if args['kategori'] is not None:
                qry_product.kategori = args['kategori']
            if args['type'] is not None:
                qry_product.type = args['type']
            if args['name'] is not None:
                qry_product.name = args['name']
            if args['harga'] is not None:
                qry_product.harga = args['harga']
            if args['brand'] is not None:
                qry_product.brand = args['brand']
            if args['detail'] is not None:
                qry_product.detail = args['detail']
            if args['tersedia'] is not None:
                qry_product.tersedia = args['tersedia']
            db.session.commit()
            return marshal(qry_product, Products.response_field), 200, {'Content-Type': 'application/json'}
        elif get_jwt_claims()['user_type'] == 'publik':
            return 'Failed to edit product, this page is not accessible.', 404, {'Content-Type': 'application/json'}    
        return 'Product with that id number is not found', 404, {'Content-Type': 'application/json'}

    @jwt_required #admin or penjual can delete products if required.  
    def delete(self, id):
        qry_del = Products.query.get(id)
        if qry_del is not None and get_jwt_claims()['user_type'] == 'penjual' or get_jwt_claims()['user_type'] == 'admin':
            db.session.delete(qry_del)
            db.session.commit()
            return 'product with id = %d has been deleted' % id, 200, {'Content-Type': 'application/json'}
        return {'status': 'ID_IS_NOT_FOUND'}, 404, {'Content-Type': 'application/json'}
        
    def patch(self):
        return 'Not yet implemented', 501

api.add_resource(ProductResource, '', '/<int:id>')


class ProductPenjualResource(Resource): 

    def __init__(self):
        pass

    @jwt_required
    def get(self, id=None):
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location='args', default=1)
            parser.add_argument('rp', type=int, location='args', default=7)
            args = parser.parse_args()
            rumus_offset = args['p'] * args['rp'] - args['rp']    
            qry = Products.query
            #if token belongs to penjual and they want to see their products only
            if get_jwt_claims()['user_type'] == 'penjual':
                qry = qry.filter_by(penjual=get_jwt_claims()['name'])
                rows = []
                for row in qry.limit(args['rp']).offset(rumus_offset).all():
                    rows.append(marshal(row, Products.response_field))
                if rows is not []:
                    return rows, 200, {'Content-Type': 'application/json'}
                return {'message': 'Barang yang anda cari tidak dapat ditemukan'}, 404, {'Content-Type': 'application/json'}
        else:
            qry = Products.query.get(id) #select * from where id = id
            if qry != None:
                return marshal(qry, Products.response_field), 200, {'Content-Type': 'application/json'}   
            return {'status': 'not found', 'message': f'Product dengan id: {id} tidak ditemukan'}, 404, {'Content-Type': 'application/json'}        

    @jwt_required 
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('kategori', location='json')
        parser.add_argument('type', location='json')
        parser.add_argument('name', location='json')
        parser.add_argument('harga', location='json')
        parser.add_argument('brand', location='json')
        parser.add_argument('detail', location='json')
        parser.add_argument('tersedia', location='json')
        args = parser.parse_args()
        qry_product = Products.query.get(id)
        #id is found and the user type is penjual or admin, put can be used. publik cannot edit product data.
        #penjual can only edit their own selling products. cannot edit other seller's products.
        if qry_product is not None and ( get_jwt_claims()['user_type'] == 'penjual' and get_jwt_claims()['name'] == qry_product.penjual ):
            # penjual or admin can edit certain type of input only, if required. E.g. : only editing the detail of products, other requirements no need to be filled.
            if args['kategori'] is not None:
                qry_product.kategori = args['kategori']
            if args['type'] is not None:
                qry_product.type = args['type']
            if args['name'] is not None:
                qry_product.name = args['name']
            if args['harga'] is not None:
                qry_product.harga = args['harga']
            if args['brand'] is not None:
                qry_product.brand = args['brand']
            if args['detail'] is not None:
                qry_product.detail = args['detail']
            if args['tersedia'] is not None:
                qry_product.tersedia = args['tersedia']
            db.session.commit()
            return marshal(qry_product, Products.response_field), 200, {'Content-Type': 'application/json'}
        elif get_jwt_claims()['user_type'] == 'publik':
            return 'Failed to edit product, this page is not accessible.', 404, {'Content-Type': 'application/json'}    
        return 'Product with that id number is not found', 404, {'Content-Type': 'application/json'}

api.add_resource(ProductPenjualResource, '/penjual', '/penjual/<int:id>')