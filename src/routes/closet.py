from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from utils.database_utils import allowed_file, save_file, save_data_to_db, get_user_clothes
from utils.embeddings_utils import get_image_embeddings,  get_clothing_type
from utils.background_utils import remove_image_background

closet_bp = Blueprint('closet', __name__)


@closet_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """allow the user to upload pictures of their clothes"""

    current_user = get_jwt_identity()
    print("USER MAKING REQUEST:", current_user)

    if 'file' not in request.files:
        return jsonify({'success': False,
                        'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False,
                        'message': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'success': False,
                        'message': 'File extension not allowed'}), 400
    
    no_background_file = remove_image_background(file)
    file_path = save_file(file, no_background_file)

    image = open(file_path, "rb")
    clothing_type = get_clothing_type(image)
    image_embeddings = get_image_embeddings(image)
    data = {
        "username": current_user["username"],
        "image_path": file_path,
        "type": clothing_type,
        "image_embeddings": image_embeddings
    }
    save_data_to_db(data, current_app.db)
    
    return jsonify({'success': True,
                    'message': 'File uploaded successfully'}), 201


@closet_bp.route('/clothes', methods=['GET'])
@jwt_required()
def get_clothes():
    """Get a list of the clothes owned by the user"""

    current_user = get_jwt_identity()
    username = current_user["username"]
    clothes = get_user_clothes(username, current_app.db)
    print("LENGTH CLOTHES", len(clothes))
    print(f"first clothes {clothes[0]['type']}")

    if len(clothes) == 0:
        return jsonify({"success": False,
                        "message": f"Could not find any clothes for user {username}"}), 400
    
    return jsonify({"success": True,
                    "clothes": clothes}), 200