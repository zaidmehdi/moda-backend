import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient

from src.utils import allowed_file, save_file, file_to_buffer,\
    get_image_embeddings, get_clothing_type, save_data_to_db


UPLOAD_FOLDER = 'images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

load_dotenv()
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

MONGO_URI = "mongodb://localhost:27017/moda"
client = MongoClient(MONGO_URI)
db = client.moda


@app.route("/register", methods=['POST'])
def register_user():
    collection = db.users
    username = request.json.get('username')

    existing_user = collection.find_one({'username': username})
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    new_user = {'_id': username, 
                "clothes": {}}
    result = collection.insert_one(new_user)
    
    return jsonify({'message': 'User registered successfully', 'user_id': str(result.inserted_id)}), 201


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'message': 'File extension not allowed'}), 400
    if 'username' not in request.form:
        return jsonify({'message': 'No username provided'}), 400
    
    file_path = save_file(file, app)

    image = open(file_path, "rb")
    clothing_type = get_clothing_type(image)
    image_embeddings = get_image_embeddings(image)
    data = {
        "username": request.form["username"],
        "image_path": file_path,
        "type": clothing_type,
        "image_embeddings": image_embeddings
    }
    save_data_to_db(data, db)
    
    return jsonify({'message': 'File uploaded successfully'}), 200


@app.route("/recommend", methods=["POST"])
def recommend_outfit():
    outfit = []

    return outfit


if __name__ == "__main__":
    app.run(debug=True)