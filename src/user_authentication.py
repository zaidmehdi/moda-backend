from flask_login import UserMixin

from main import user_db


class Users(UserMixin, user_db.Model):
    id = user_db.Column(user_db.Integer, primary_key=True)
    username = user_db.Column(user_db.String(250), unique=True, nullable=False)
    password = user_db.Column(user_db.String(250), nullable=False)