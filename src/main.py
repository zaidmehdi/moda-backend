import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from openai import OpenAI
from pymongo import MongoClient

from src.utils import allowed_file, save_file, get_image_embeddings, \
    get_clothing_type, save_data_to_db, fetch_weather, get_gender_by_username, \
    prompt_gpt, get_outfit


UPLOAD_FOLDER = 'images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
user_db = SQLAlchemy()
login_manager = LoginManager()
login_manager.init_app(app)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.moda



@app.route("/register", methods=['POST'])
def register_user():
    collection = db.users
    username = request.json.get('username')
    gender = request.json.get("gender")

    existing_user = collection.find_one({'_id': username})
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    new_user = {'_id': username, 
                'gender': gender,
                "closet": {}}
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
    """Takes as input a username, a context, latitude, and longitude"""
    username = request.json.get('username')
    context = request.json.get('context')
    temperature = fetch_weather(float(request.json.get("latitude")), float(request.json.get("longitude")))
    gender = get_gender_by_username(username, db)

    outfit_description = prompt_gpt(openai_client, gender, context, temperature)
    outfit = get_outfit(outfit_description, username, db)

    return jsonify({'outfit': outfit, 'message': "Recommendation Successful"}), 200


if __name__ == "__main__":
    app.run(debug=True)