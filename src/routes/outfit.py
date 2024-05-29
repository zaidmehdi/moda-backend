from flask import Blueprint, jsonify, current_app, request
from flask_login import login_required

from utils.context_utils import fetch_weather, get_gender_by_username
from utils.outfit_utils import get_outfit_description, get_outfit


outfit_bp = Blueprint('outfit', __name__)


@outfit_bp.route("/recommend", methods=["POST"])
@login_required
def recommend_outfit():
    """Takes as input a username, a context, latitude, and longitude"""

    username = request.json.get('username')
    context = request.json.get('context')
    temperature = fetch_weather(float(request.json.get("latitude")), float(request.json.get("longitude")))
    gender = get_gender_by_username(username, current_app.db)

    outfit_description = get_outfit_description(current_app.openai_client, gender, context, temperature)
    outfit = get_outfit(outfit_description, username, current_app.db)

    return jsonify({'outfit': outfit, 'message': "Recommendation Successful"}), 200
