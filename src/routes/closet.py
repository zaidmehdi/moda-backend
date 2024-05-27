from flask import Blueprint, jsonify, current_app, request

from utils.database_utils import allowed_file, save_file, save_data_to_db
from utils.embeddings_utils import get_image_embeddings,  get_clothing_type
from utils.background_utils import remove_image_background

closet_bp = Blueprint('closet', __name__)


@closet_bp.route('/upload', methods=['POST'])
def upload_file():
    """allow the user to upload pictures of their clothes"""

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
    if 'username' not in request.form:
        return jsonify({'success': False,
                        'message': 'No username provided'}), 400
    
    no_bakcground_file = remove_image_background(file)
    file_path = save_file(no_bakcground_file, closet_bp)

    image = open(file_path, "rb")
    clothing_type = get_clothing_type(image)
    image_embeddings = get_image_embeddings(image)
    data = {
        "username": request.form["username"],
        "image_path": file_path,
        "type": clothing_type,
        "image_embeddings": image_embeddings
    }
    save_data_to_db(data, current_app.db)
    
    return jsonify({'success': True,
                    'message': 'File uploaded successfully'}), 201
