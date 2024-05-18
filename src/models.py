import bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


user_db = SQLAlchemy()

class Users(UserMixin, user_db.Model):
    id = user_db.Column(user_db.Integer, primary_key=True)
    username = user_db.Column(user_db.String(250), unique=True, nullable=False)
    gender = user_db.Column(user_db.String(10), nullable=False)
    email = user_db.Column(user_db.String(250), unique=True, nullable=False)
    password_hash = user_db.Column(user_db.String(250), nullable=False)

    def set_password(self, password):
        """Hash the password and store the hash."""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Check the hashed password."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))