'''ímport dependancies'''
import datetime
from flask import jsonify, Blueprint, request, Flask
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity,
    create_access_token, get_raw_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from hello_books import app, jwt
from hello_books.api.models import HelloBooks

blacklist = set()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    '''check if token is blacklisted'''
    jti = decrypted_token['jti']
    return jti in blacklist

auth = Blueprint('auth', __name__)
hello_books = HelloBooks()

@app.route('/', methods=['GET'])
def home():
    '''Home page containing link to documentation'''
    return jsonify(
        {'Hello Books API': "Click here to see documentation -> https://hellobooks8.docs.apiary.io/"})

@app.route('/api/v1/auth/reset-password', methods=['POST'])
def reset_password():
    '''Function to reseta user password'''
    email = request.json.get('email').strip()
    for user in hello_books.users_list:
        if email == user['email']:
            user['password'] = generate_password_hash("Pass123")
            return jsonify({
                'message': "Password has been changed to Pass123. Please login and change it."
            }), 201
    return jsonify({'message': 'Email not found.'}), 404

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    '''Fuction to register a new user'''
    try:
        sent_data = request.get_json(force=True)
        raw_data = {
            'name': sent_data['name'],
            'email': sent_data['email'],
            'password': sent_data['password']
        }
        data = {k.strip(): v.strip() for k, v in raw_data.items()}
        if hello_books.check_email_exists(data['email']):
            return jsonify({'message': 'Email Exists'})
        else:
            if hello_books.user_data_validation(data) == True:
                return hello_books.user_registration(data), 201
            else:
                return jsonify(
                    {'message': 'Please enter all the data in the correct format.'})
    except BaseException:
        return jsonify({'message': "Data has not been input correctly."})

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    '''Function for logging in'''
    try:
        sent_data = request.get_json(force=True)
        raw_data = {
            'email': sent_data['email'],
            'password': sent_data['password']
        }
        data = {k.strip(): v.strip() for k, v in raw_data.items()}
        return hello_books.user_login(data), 200
    except BaseException:
        return jsonify(
            {'message': 'Please enter your email and password correctly'})

@app.route('/api/v1/auth/logout', methods=['GET', 'POST'])
@jwt_required
def logout():
    '''Function for logout'''
    token_identifier = get_raw_jwt()['jti']
    blacklist.add(token_identifier)
    return jsonify({'message': 'You are now logged out'}), 200

@app.route('/api/v1/auth/change-password', methods=['PUT'])
@jwt_required
def change_password():
    '''Function for changing user password'''
    email = get_jwt_identity()
    new_password = request.json.get('new_password').strip()
    old_password = request.json.get('old_password').strip()
    for user in hello_books.users_list:
        if email == user['email']:
            if hello_books.password_validation({"password": new_password}) == True:
                if check_password_hash(user['password'], old_password):
                    user['password'] = generate_password_hash(new_password)
                    return jsonify(
                        {'message': "Password has been changed"}), 201
                else:
                    return jsonify({"message": "Old password does not match"}), 401
            else:
                return jsonify(
                    {'message': "Password needs to be 6 characters or more"})
    return jsonify({'message': 'Unable to change password.'})


@app.route('/api/v1/auth/users')
@jwt_required
def view_users():
    '''Function for viewing all books'''
    return hello_books.view_users(), 200

