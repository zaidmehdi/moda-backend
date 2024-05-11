import os
import sys
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, logout_user
from openai import OpenAI
from pymongo import MongoClient

from user_authentication import Users, user_db
from utils.context_utils import fetch_weather, get_gender_by_username
from utils.database_utils import allowed_file, save_file, save_data_to_db
from utils.embeddings_utils import get_image_embeddings,  get_clothing_type
from utils.outfit_utils import get_outfit_description, get_outfit


UPLOAD_FOLDER = 'images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLITE_URI")
app.config["SECRET_KEY"] = os.getenv("SQLITE_KEY")

login_manager = LoginManager()
login_manager.init_app(app)

user_db.init_app(app)
with app.app_context():
    user_db.create_all()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.moda


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route('/register', methods=["POST"])
def register():
    """When user registers, create account in the sqlite db with password, 
    and create an entry in mongodb to store the closet"""

    collection = db.users
    username = request.json.get('username')
    gender = request.json.get("gender")

    existing_user = collection.find_one({'_id': username})
    if existing_user:
        return jsonify({"success": False,
                        'message': 'Username already exists'}), 400

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


@app.route("/login", methods=["POST"])
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


@app.route("/logout")
def logout():
    """allow the user to logout"""

    logout_user()

    return jsonify({
        "success": True,
        "message": "Successfully logged out (or already logged out)"
        }), 200


@app.route('/upload', methods=['POST'])
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
    
    return jsonify({'success': True,
                    'message': 'File uploaded successfully'}), 200


@app.route("/recommend", methods=["POST"])
def recommend_outfit():
    """Takes as input a username, a context, latitude, and longitude"""

    username = request.json.get('username')
    context = request.json.get('context')
    temperature = fetch_weather(float(request.json.get("latitude")), float(request.json.get("longitude")))
    gender = get_gender_by_username(username, db)

    outfit_description = get_outfit_description(openai_client, gender, context, temperature)
    outfit = get_outfit(outfit_description, username, db)

    return jsonify({'outfit': outfit, 'message': "Recommendation Successful"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
