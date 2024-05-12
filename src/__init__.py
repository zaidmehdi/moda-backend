import os

from dotenv import load_dotenv
from flask import Flask, current_app
from flask_login import LoginManager
from openai import OpenAI
from pymongo import MongoClient

from user_authentication import Users, user_db


def create_app(config_name='development'):
    """Initialize the app with correct configuration"""

    app = Flask(__name__)

    load_dotenv('.flaskenv')
    load_dotenv('.env')

    app.config["SECRET_KEY"] = os.getenv("SQLITE_KEY")
    app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLITE_URI")

    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    client = MongoClient(os.getenv("MONGO_URI"))
    db = client.moda

    login_manager = LoginManager()
    login_manager.init_app(app)

    if config_name == "production":
        app.config['PORT'] = os.getenv("FLASK_PORT_PROD")
    else:
        app.config['PORT'] = os.getenv("FLASK_PORT")

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