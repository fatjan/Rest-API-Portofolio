import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from . import *
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims

bp_user = Blueprint('user', __name__)
api = Api(bp_user)

class UserResource(Resource): 

    def __init__(self):
        pass
       
    @jwt_required  #for admin to see all users 
    def get(self):
        if get_jwt_claims()['user_type'] == 'admin':
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location='args', default=1)
            parser.add_argument('rp', type=int, location='args', default=5)
            parser.add_argument('user_type', location='args')
            parser.add_argument('username', location='args')
            parser.add_argument('name', location='args')
            parser.add_argument('address', location='args')
            parser.add_argument('kota', location='args')
            args = parser.parse_args()
            rumus_offset = args['p'] * args['rp'] - args['rp']
            qry = Users.query
            if args['user_type'] is not None:
                qry = qry.filter_by(user_type=args['user_type']) #qry that is filtered by name >> for exact name
            if args['username'] is not None:
                qry = qry.filter(Users.username.like("%"+args['username']+"%")) #for name with this name, and not case sensitive
            if args['name'] is not None:
                qry = qry.filter(Users.name.like("%"+args['name']+"%"))
            if args['address'] is not None:
                qry = qry.filter(Users.address.like("%"+args['address']+"%"))
            if args['kota'] is not None:
                qry = qry.filter(Users.kota.like("%"+args['kota']+"%"))    
            rows = []
            for row in qry.limit(args['rp']).offset(rumus_offset).all():
                rows.append(marshal(row, Users.response_field))
            return {"status":"200 OK", "message": "all users are on display", "users": rows}, 200, {'Content-Type': 'application/json'}
        else:
            id = get_jwt_claims()['id']
            qry = Users.query.get(id) #select * from where id = id
            return {"status": "200 OK", "message": "Your user profile is on display", "user": marshal(qry, Users.response_field)}, 200, {'Content-Type': 'application/json'}   
            #penjual and publik can only see their own user profile

    def post(self): #for everyone to register and login        
        parser = reqparse.RequestParser()
        parser.add_argument('user_type', location='args')
        parser.add_argument('username', location='json')
        parser.add_argument('name', location='json')
        parser.add_argument('password', location='json')
        parser.add_argument('address', location='json')
        parser.add_argument('kota', location='json')
        args = parser.parse_args() #this becomes str_serialized
        if args['user_type'] is None:
            args['user_type'] = 'publik'
        user_new = Users(None, args['user_type'], args['username'], args['name'] , args['password'], args['address'], args['kota'])
        db.session.add(user_new) #insert the input data into the database
        db.session.commit() 
        return {"code": 200, "message": "OK, your user profile has been created", "data":marshal(user_new, Users.response_field)}, 200, {'Content-Type': 'application/json'}   
    
    @jwt_required #if user wants to change their profile details
    #user can only change their own profile. not someone else's
    #admin can also edit user's profile if needed.
    def put(self, id):

        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json')
        parser.add_argument('name', location='json')
        parser.add_argument('password', location='json')
        parser.add_argument('address', location='json')
        parser.add_argument('kota', location='json')
        args = parser.parse_args()
        qry_user = Users.query.get(id)
        if qry_user is not None and get_jwt_claims()['id'] == id or get_jwt_claims()['user_type'] == 'admin':
            if args['username'] is not None:
                qry_user.username = args['username']
            if args['name'] is not None:
                qry_user.name = args['name']
            if args['password'] is not None:
                qry_user.password = args['password']
            if args['address'] is not None:
                qry_user.address = args['address']
            if args['kota'] is not None:
                qry_user.kota = args['kota']
            db.session.commit()
            return marshal(qry_user, Users.response_field), 200, {'Content-Type': 'application/json'}
        elif qry_user is not None and get_jwt_claims()['id'] != id:
            return 'Failed to change profile. You can only change your own profile. Kindly check again your own user id number', 404, {'Content-Type': 'application/json'}
        return 'Failed to edit profile. Wrong username or password', 404, {'Content-Type': 'application/json'}

    @jwt_required #delete user is only for admin if any users do some violation of use.  
    #or if the user itself wants to delete profile due to their own willingness to delete their profile.
    def delete(self, id):
        qry_del = Users.query.get(id)
        if qry_del is not None: 
            if get_jwt_claims()['user_type'] == 'admin':
                db.session.delete(qry_del)
                db.session.commit()
                return 'User with id = %d has been deleted' % id, 200, {'Content-Type': 'application/json'}
            elif get_jwt_claims()['id'] == 'id':
                db.session.delete(qry_del)
                db.session.commit()
                return 'Your profile with id = %d has been deleted' % id, 200, {'Content-Type': 'application/json'}
        elif get_jwt_claims()['user_type'] != 'admin' or get_jwt_claims()['id'] == 'id':
            return 'Failed to delete the profile. You do not have permission to delete this profile.', 404, {'Content-Type': 'application/json'}
        return {'status': 'ID_IS_NOT_FOUND'}, 404, {'Content-Type': 'application/json'}
        
    def patch(self):
        return 'Not yet implemented', 501

api.add_resource(UserResource, '', '/<int:id>')
