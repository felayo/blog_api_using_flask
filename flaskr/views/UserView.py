from flask import Flask, request, json, Response, Blueprint, g, jsonify
from marshmallow import ValidationError
from ..models import UserModel, UserSchema
from ..shared.Authentication import auth_required

import os
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
user_api = Blueprint('user_api', __name__)
user_schema = UserSchema()


@user_api.route('/', methods=['POST'])
def create():
    """
    Create User Function
    """
    req_data = request.get_json()
    app.logger.info('llega siquiera --------------#'+json.dumps(req_data))

    try:
        data = user_schema.load(req_data)
        
    except ValidationError as err:
        return custom_response(err, 400)
    
    # Check to ensure the password length is equal or greater than 6
    if len(data.get('password')) < 6:
        return custom_response({'error': 'Password must be at least 6 characters'}, 422)
    
    # check if user already exist in the db
    user_in_db = UserModel.get_user_by_email(data.get('email'))
    if user_in_db:
        message = {
            'error': 'User already exist, please supply another email address'}
        return custom_response(message, 400)

    user = UserModel(data)
    
    user.save()

    #ser_data = user_schema.dump(user)

    #token = Auth.generate_token(ser_data.get('id'))
    
    token = jwt.encode(
        {"id": user.id, "exp": datetime.now() + timedelta(days=1)},
        os.environ.get("JWT_SECRET_KEY"),
        algorithm="HS256",
    )

    #return custom_response({'jwt_token': token}, 201)
    
    return jsonify({
        "success": True,
        "jwt_token": token
    })

    


@user_api.route('/', methods=['GET'])
@auth_required
def get_all():
    users = UserModel.get_all_users()
    ser_users = user_schema.dump(users, many=True)
    return custom_response(ser_users, 200)


@user_api.route('/login', methods=['POST'])
def login():
    """
    User Login Function
    """
    req_data = request.get_json()
    app.logger.info('llega siquiera --------------#'+json.dumps(req_data))

    try:
        data = user_schema.load(req_data, partial=True)
    except ValidationError as err:
        return custom_response(err, 400)

    if not data.get('email') or not data.get('password'):
        return custom_response({'error': 'you need email and password to sign in'}, 400)

    user = UserModel.get_user_by_email(data.get('email'))
    if not user:
        return custom_response({'error': 'invalid credentials'}, 400)
    if not user.check_hash(data.get('password')):
        return custom_response({'error': 'invalid credentials'}, 400)

    #ser_data = user_schema.dump(user)

    token = jwt.encode(
        {"id": user.id, "exp": datetime.now() + timedelta(days=1)},
        os.environ.get("JWT_SECRET_KEY"),
        algorithm="HS256",
    )

    return custom_response({'jwt_token': token}, 200)


@user_api.route('/loginfg', methods=['POST'])
def loginfg():
    """
    User Login Function
    """
    req_data = request.get_json()
    app.logger.info('llega siquiera --------------#'+json.dumps(req_data))

    try:
        data = user_schema.load(req_data, partial=True)
    except ValidationError as err:
        return custom_response(err, 400)

    if not data.get('email') or not data.get('tokenfg'):
        return custom_response({'error': 'you need email and token from facebook/gmail to sign in'}, 400)

    user = UserModel.get_user_by_email(data.get('email'))
    if not user:
        return custom_response({'error': 'email does not exist'}, 400)
    # if not user.check_hash(data.get('password')):
    #     return custom_response({'error': 'invalid credentials'}, 400)
    # Aqui en vez de revisar password revisamos contra feis y google q si funcione el token válido

    ser_data = user_schema.dump(user)

    token = Auth.generate_token(ser_data.get('id'))

    return custom_response({'jwt_token': token}, 200)


@user_api.route('/<int:user_id>', methods=['GET'])
@auth_required
def get_a_user(user_id):
    """
    Get a single user
    """
    user = UserModel.get_one_user(user_id)
    if not user:
        return custom_response({'error': 'user not found'}, 404)

    ser_user = user_schema.dump(user)   # ser_user means serialise user
    return custom_response(ser_user, 200)


@user_api.route('/me', methods=['PUT'])
@auth_required
def update():
    """
    Update me
    """
    req_data = request.get_json()
    try:
        data = user_schema.load(req_data, partial=True)
    except ValidationError as err:
        return custom_response(err, 400)

    user = UserModel.get_one_user(g.user.get("id"))
    user.update(data)
    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)


@user_api.route('/me', methods=['DELETE'])
@auth_required
def delete():
    """
    Delete a user
    """
    user = UserModel.get_one_user(g.user.get('id'))
    user.delete()
    return custom_response({'message': 'deleted'}, 204)


@user_api.route('/me', methods=['GET'])
@auth_required
def get_me():
    """
    Get me
    """
    user = UserModel.get_one_user(g.user.get('id'))
    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)


def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
