import os
import sys
import tempfile

from dotenv import load_dotenv
from flask import Flask, current_app
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_migrate import Migrate
from openai import OpenAI
from pymongo import MongoClient

sys.path.append(os.path.dirname(__file__))
from models import Users, user_db


def create_app(config_name='development'):
    """Initialize the app with correct configuration"""

    app = Flask(__name__)
    Migrate(app, user_db)

    load_dotenv('.flaskenv')
    load_dotenv('.env')

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

    jwt = JWTManager(app)

    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    client = MongoClient(os.getenv("MONGO_URI"))
    db = client.moda

    login_manager = LoginManager()
    login_manager.init_app(app)

    if config_name == "production":
        app.config['PORT'] = os.getenv("FLASK_PORT_PROD")
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_PREFIX") + \
            os.path.join(os.getcwd(), os.getenv("DATABASE_URI"))

    elif config_name == "testing":
        app.config['PORT'] = os.getenv("FLASK_PORT")
        _,  db_path = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_PREFIX") + db_path

    else:
        app.config['PORT'] = os.getenv("FLASK_PORT")
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_PREFIX") + \
            os.path.join(os.getcwd(), os.getenv("DATABASE_URI"))

    print(f'DATABASE: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    user_db.init_app(app)
    with app.app_context():
        user_db.create_all()
        current_app.user_db = user_db
        current_app.db = db
        current_app.openai_client = openai_client

        @login_manager.user_loader
        def loader_user(user_id):
            return Users.query.get(user_id)

    return app