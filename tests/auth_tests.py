import os
import random
import string
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.__init__ import create_app
from src.routes.auth import auth_bp


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        """Set up the app for testing environment"""

        self.app = create_app(config_name="testing")        
        self.app.register_blueprint(auth_bp)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.collection = self.client.application.db.users

        with self.app.app_context():
            self._send_register_post_request(username="test_user")
    

    def tearDown(self):
        """Clean up after the test"""

        self.app.user_db.session.rollback()
        self.app_context.pop()


    def _generate_random_string(self, length=16):
        """Generate a random string of letters and digits"""

        characters = string.ascii_letters + string.digits

        return ''.join(random.choice(characters) for _ in range(length))


    def _delete_from_mongodb(self, username):
        """Delete the user from mongodb (after testing registration)
        because it is not rolled back automatically by flask, unlike sqlite"""
        
        self.collection.delete_one({"_id": username})

    
    def _send_register_post_request(self, username):
        """Method to send a post request to the /register endpoint
        and delete the user's entry from mongodb"""

        password = self._generate_random_string()

        data = {
            "username": username,
            "password": password,
            "gender": "male"
        }

        response = self.client.post("/register", json=data)
        self._delete_from_mongodb(username)

        return response
    

    def _send_login_post_request(self, username, password):
        """Method to send a post request to the /login endpoint"""

        data = {
            "username": username,
            "password": password
        }

        return self.client.post("/login", json=data)
    

    def test_register_success(self):
        """Test registration (/register) with valid data"""
        
        username = self._generate_random_string()
        response = self._send_register_post_request(username)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["message"], "User successfully registered")
        self.assertEqual(response.json["user_id"], username)

    
    def test_register_existing_user(self):
        """Test registration (/register) with a user that already exists"""

        username = "test_user"
        response = self._send_register_post_request(username)

        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.json["success"])
        self.assertEqual(response.json["message"], "Username already exists")



if __name__ == "__main__":
    unittest.main()