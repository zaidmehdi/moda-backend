import os
import random
import string
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.main import app, db



class TestRegisterEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.collection = db.users


    def _generate_random_string(self, length=16):
        """Generate a random string of letters and digits"""

        characters = string.ascii_letters + string.digits

        return ''.join(random.choice(characters) for _ in range(length))


    def _delete_from_mongodb(self, username):
        """Delete the user from mongodb (after testing registration)
        because it is not rolled back automatically by flask, unlike sqlite"""
        
        self.collection.delete_one({"_id": username})


    def test_register_success(self):
        """Test registration with valid data"""
        
        username = self._generate_random_string()
        password = self._generate_random_string()

        data = {
            "username": username,
            "password": password,
            "gender": "male"
        }

        response = self.app.post("/register", json=data)
        self._delete_from_mongodb(username)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["message"], "User successfully registered")
        self.assertEqual(response.json["user_id"], username)



if __name__ == "__main__":
    unittest.main()