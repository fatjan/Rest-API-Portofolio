import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from blueprints.user import *

bp_login = Blueprint('login', __name__)
api = Api(bp_login)

class CreateTokenResources(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()
        # if args['user_type'] == None:
        #     args['user_type'] = 'publik'
        qry = Users.query.filter_by(username=args['username']).filter_by(password=args['password']).first()
        if qry is not None:    
            token = create_access_token(identity=marshal(qry, Users.response_field))
            return {'token': token}, 200
        else:
            return {'status': 'UNAUTHORIZED', 'message': 'invalid name or password'}, 401

api.add_resource(CreateTokenResources, '')