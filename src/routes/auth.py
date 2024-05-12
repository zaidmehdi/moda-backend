from flask import Blueprint, jsonify, current_app, request
from flask_login import login_user, logout_user

from models import Users, user_db


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=["POST"])
def register():
    """When user registers, create account in the sqlite db with password, 
    and create an entry in mongodb to store the closet"""

    collection = current_app.db.users
    username = request.json.get('username')
    gender = request.json.get("gender")

    existing_user = collection.find_one({'_id': username})
    if existing_user:
        return jsonify({"success": False,
                        'message': 'Username already exists'}), 409

    user = Users(username=username,
                    password=request.json.get("password"))
    user_db.session.add(user)
    user_db.session.commit()

    new_user = {'_id': username, 
                'gender': gender,
                "closet": {}}
    collection.insert_one(new_user)

    return jsonify({
        "success": True,
        "message": "User successfully registered",
        "user_id": username
        }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """allow the user to login"""

    username = request.form.get("username")
    password = request.form.get("password")

    user = Users.query.filter_by(username=username).first()

    if user and user.password == password:
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
