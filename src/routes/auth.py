from flask import Blueprint, jsonify, current_app, request
from flask_login import login_user, logout_user
from sqlalchemy.exc import IntegrityError

from models import Users, user_db
from utils.auth_utils import validate_email


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=["POST"])
def signup():
    """When user signs up, create account in the sqlite db with password, 
    and create an entry in mongodb to store the closet"""

    collection = current_app.db.users
    username = request.json.get('username')
    gender = request.json.get("gender")
    email = request.json.get("email")
    password=request.json.get("password")

    if not validate_email(email):
        return jsonify({
            "success": False,
            "message": "Invalid email format"
        }), 400

    existing_user = collection.find_one({'_id': email})
    if existing_user:
        return jsonify({
            "success": False,
            'message': 'User already exists'
        }), 409

    user = Users(
            username=username,
            gender=gender,
            email=email,         
        )
    user.set_password(password)

    user_db.session.add(user)
    try:
        user_db.session.commit()
    except IntegrityError:
        return jsonify({
            "success": False,
            'message': 'User already exists'
        }), 409

    new_user = {'_id': email, 
                'gender': gender,
                "closet": {}}
    collection.insert_one(new_user)

    return jsonify({
        "success": True,
        "message": "User successfully registered",
        "username": username
        }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """allow the user to login"""

    email = request.json.get("email")
    password = request.json.get("password")

    user = Users.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            "success": True,
            "message": "User successfully logged in"
            }), 200
    
    return jsonify({
        "success": False,
        "message": "Invalid username or password"
        }), 401


@auth_bp.route("/logout")
def logout():
    """allow the user to logout"""

    logout_user()

    return jsonify({
        "success": True,
        "message": "Successfully logged out (or already logged out)"
        }), 200
