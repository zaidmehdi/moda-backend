import os
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
            self._send_signup_post_request(username="test_user", email="test.email@gmail.com", password="test_password")
    

    def tearDown(self):
        """Clean up after the test"""

        self.app.user_db.session.rollback()
        self.app_context.pop()


    def _delete_from_mongodb(self, username):
        """Delete the user from mongodb (after testing registration)
        because it is not rolled back automatically by flask, unlike sqlite"""
        
        self.collection.delete_one({"_id": username})

    
    def _send_signup_post_request(self, username, email, password):
        """Method to send a post request to the /signup endpoint
        and delete the user's entry from mongodb"""

        data = {
            "username": username,
            "gender": "male",
            "email": email,
            "password": password,
        }

        response = self.client.post("/signup", json=data)
        self._delete_from_mongodb(username)

        return response
    

    def _send_login_post_request(self, email, password):
        """Method to send a post request to the /login endpoint"""

        data = {
            "email": email,
            "password": password
        }
        
        return self.client.post("/login", json=data)
    

    def test_signup_success(self):
        """Test signup (/signup) with valid data"""
        
        username = "new_user"
        email = "new.user@gmail.com"
        password = "new_password"
        response = self._send_signup_post_request(username, email, password)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["message"], "User successfully registered")
        self.assertEqual(response.json["username"], username)

    
    def test_signup_existing_user(self):
        """Test registration (/signup) with a user that already exists"""

        username = "test_user"
        email = "test.email@gmail.com"
        password = 'test_password'
        response = self._send_signup_post_request(username, email, password)

        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.json["success"])
        self.assertEqual(response.json["message"], "User already exists")

    
    def test_login_success(self):
        """Test the login functionality of existing user"""

        email = "test.email@gmail.com"
        password = "test_password"

        response = self._send_login_post_request(email, password)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["message"], "User successfully logged in")

    
    def test_login_wrong_password(self):
        """Test the login functionality with a wrong password"""

        email = "test.email@gmail.com"
        password = "wrong_password"

        response = self._send_login_post_request(email, password)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json["success"])
        self.assertEqual(response.json["message"], "Invalid email or password")


    def test_login_inexistant_user(self):
        """Test the login functionality with user that doesn't exist"""

        email = "inexistant.user@gmail.com"
        password = "test_password"

        response = self._send_login_post_request(email, password)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json["success"])
        self.assertEqual(response.json["message"], "Invalid email or password")



if __name__ == "__main__":
    unittest.main()