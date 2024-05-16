# API endpoints

1. `/signup`
2. `/login`
3. `/logout`
4. `/upload`
5. `/recommend`

## 1. `/signup`
- **Method:** POST
- **Description:** Allows a user to signup by creating an account in the SQLite database with a password and creating an entry in MongoDB to store the user's closet.
- **Request Body:**
    - `username` (string): Username of the user registering.
    - `password` (string): Password chosen by the user.
    - `gender` (string): Gender of the user.
- **Response:**
    - Success (201):
        - `success` (boolean): Indicates if the operation was successful.
        - `message` (string): Message indicating successful registration.
        - `user_id` (string): Username of the registered user.
    - Failure (409):
        - `success` (boolean): Indicates if the operation was successful.
        - `message` (string): Error message indicating the reason for failure.

## 2. `/login`
- **Method:** POST
- **Description:** Allows a registered user to log in.
- **Request Body:**
    - `username` (string): Username of the user.
    - `password` (string): Password of the user.
- **Response:**
    - Success (200):
        - `success` (boolean): Indicates if the login was successful.
        - `message` (string): Message indicating successful login.
    - Failure (401):
        - `success` (boolean): Indicates if the login was unsuccessful.
        - `message` (string): Error message indicating invalid username or password.

## 3. `/logout`
- **Method:** GET
- **Description:** Allows a logged-in user to log out.
- **Response:**
    - Success (200):
        - `success` (boolean): Indicates if the logout was successful.
        - `message` (string): Message indicating successful logout.

## 4. `/upload`
- **Method:** POST
- **Description:** Allows a user to upload pictures of their clothes.
- **Request Body:**
    - `file` (file): Image file of the clothing.
    - `username` (string): Username of the user uploading the file.
- **Response:**
    - Success (201):
        - `success` (boolean): Indicates if the upload was successful.
        - `message` (string): Message indicating successful file upload.
    - Failure (400):
        - `success` (boolean): Indicates if the upload was successful.
        - `message` (string): Error message indicating the reason for failure.

## 5. `/recommend`
- **Method:** POST
- **Description:** Provides outfit recommendations for a user based on various factors such as context, weather, and gender.
- **Request Body:**
    - `username` (string): Username of the user.
    - `context` (string): Context for the outfit recommendation.
    - `latitude` (float): Latitude coordinate for weather information.
    - `longitude` (float): Longitude coordinate for weather information.
- **Response:**
    - Success (200):
        - `outfit` (object): Recommended outfit details.
        - `message` (string): Message indicating successful recommendation.