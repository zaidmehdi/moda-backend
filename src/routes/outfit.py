from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from utils.context_utils import fetch_weather, get_gender_by_username
from utils.outfit_utils import get_outfit_description, get_outfit


outfit_bp = Blueprint('outfit', __name__)


@outfit_bp.route("/recommend", methods=["POST"])
@jwt_required()
def recommend_outfit():
    """Takes as input a username, a context, latitude, and longitude"""

    current_user = get_jwt_identity()
    print("USER MAKING REQUEST:", current_user)

    username = current_user['username']
    context = request.json.get('context')
    temperature = fetch_weather(float(request.json.get("latitude")), float(request.json.get("longitude")))
    gender = get_gender_by_username(username, current_app.db)

    outfit_description = get_outfit_description(current_app.openai_client, gender, context, temperature)
    outfit = get_outfit(outfit_description, username, current_app.db)

    return jsonify({'outfit': outfit, 'message': "Recommendation Successful"}), 200
