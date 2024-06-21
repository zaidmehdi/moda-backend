# API endpoints

1. `/signup`
2. `/login`
3. `/upload`
4. `/clothes`
5. `/images/<filename>`
6. `/recommend`

## 1. `/signup`
- **Method:** POST
- **Description:** Allows a user to signup by creating an account in the SQLite database with a password and creating an entry in MongoDB to store the user's closet.
- **Request Body:**
    - `username` (string): Username of the user.
    - `gender` (string): Gender of the user.
    - `email` (string): Email address of the user.
    - `password` (string): Password chosen by the user.
- **Response:**
    - Success (201):
        - `success` (boolean): Indicates if the operation was successful.
        - `message` (string): Message indicating successful registration.
        - `username` (string): Username of the registered user.
    - Failure (409):
        - `success` (boolean): Indicates if the operation was successful.
        - `message` (string): Error message indicating the reason for failure.
- **Curl Command:**
```
curl -X POST \
  http://<server_address>/signup \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "test_username",
    "gender": "male",
    "email": "test_email@example.com",
    "password": "test_password"
}'
```

## 2. `/login`
- **Method:** POST
- **Description:** Allows a registered user to log in.
- **Request Body:**
    - `email` (string): Email address of the user.
    - `password` (string): Password of the user.
- **Response:**
    - Success (200):
        - `success` (boolean): Indicates if the login was successful.
        - `message` (string): Message indicating successful login.
    - Failure (401):
        - `success` (boolean): Indicates if the login was unsuccessful.
        - `message` (string): Error message indicating invalid username or password.
- **Curl Command:**
```
curl -X POST \
    http://<server_address>/login \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test_email@example.com", 
        "password": "test_password"
        }'
```

## 3. `/upload`
- **Method:** POST
- **Description:** Allows a user to upload pictures of their clothes.
- **Headers:**
    - `Authorization` (string): Bearer token obtained after login.
- **Request Body:**
    - `file` (file): Image file of the clothing.
- **Response:**
    - Success (201):
        - `success` (boolean): Indicates if the upload was successful.
        - `message` (string): Message indicating successful file upload.
    - Failure (400):
        - `success` (boolean): Indicates if the upload was successful.
        - `message` (string): Error message indicating the reason for failure.
- **Curl Command:**
```
curl -X POST \
  http://<server_address>/upload \
  -H 'Authorization: Bearer <YOUR_JWT_TOKEN>' \
  -F 'file=@</path/to/your/file.jpg>'
```

## 4. `/clothes`
- **Method:** GET
- **Description:** Get a list of the clothes owned by the authenticated user (type and image path).
- **Headers:**
    - `Authorization` (string): Bearer token obtained after login.
- **Response:**
    - Success (200):
        - `success` (boolean): Indicates if the request was successful.
        - `clothes` (list): List of the clothes where every element is a dictionary containing the `type` (tops, bottoms, shoes, outerwear) and the `path` (url of the image)
    - Failure (400):
        - `success` (boolean): Indicates if the request was successful.
        - `message` (string): Failure message.
- **Curl Command:**
```
curl -X GET \
    http://<server_address>/clothes \
     -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

## 5. `/images/<filename>`
- **Method:** GET
- **Description:** Get an image from the storage.
- **Headers:**
    - `Authorization` (string): Bearer token obtained after login.
- **Response:**
    - Success (200):
    - Failure (403):
- **Curl Command:**
```
curl -X GET \
    -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
    http://<server_address>/images/<filename>
```

## 6. `/recommend`
- **Method:** POST
- **Description:** Provides outfit recommendations for a user based on various factors such as context, weather, and gender.
- **Headers:**
    - `Authorization` (string): Bearer token obtained after login.
- **Request Body:**
    - `context` (string): Context for the outfit recommendation.
    - `latitude` (float): Latitude coordinate for weather information.
    - `longitude` (float): Longitude coordinate for weather information.
- **Response:**
    - Success (200):
        - `outfit` (object): Recommended outfit details.
        - `message` (string): Message indicating successful recommendation.
- **Curl Command:**
```
curl -X POST \
  http://<server_address>/recommend \
  -H 'Authorization: Bearer <YOUR_JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "context": "casual",
    "latitude": "40.7128",
    "longitude": "-74.0060"
}'
```
