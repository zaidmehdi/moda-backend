import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename

from src.utils import allowed_file, image_to_buffer, get_image_description


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
    
    filename = secure_filename(file.filename)
    # In case there is a duplicate
    name, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        filename = f"{name}_{counter}{extension}"
        counter += 1

    file_buffered = image_to_buffer(file)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    description = get_image_description(file_buffered)
    print(description)
    
    return jsonify({'message': 'File uploaded successfully'}), 200


@app.route("/recommend", methods=["POST"])
def recommend_outfit():
    outfit = []

    return outfit


if __name__ == "__main__":
    app.run(debug=True)