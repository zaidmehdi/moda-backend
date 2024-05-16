from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


user_db = SQLAlchemy()

class Users(UserMixin, user_db.Model):
    id = user_db.Column(user_db.Integer, primary_key=True)
    username = user_db.Column(user_db.String(250), unique=True, nullable=False)
    gender = user_db.Column(user_db.String(10), nullable=False)
    email = user_db.Column(user_db.String(250), unique=True, nullable=False)
    password = user_db.Column(user_db.String(250), nullable=False)