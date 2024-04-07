import os

import replicate
from io import BytesIO
from pymongo import MongoClient
from werkzeug.utils import secure_filename


CLOTHES_TYPES = ["tops", "bottoms", "shoes", "outerwear"]


def allowed_file(filename):
    """Checks if uploaded file is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, app):
    """Makes filename unique and saves it"""
    filename = secure_filename(file.filename)
    name, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        filename = f"{name}_{counter}{extension}"
        counter += 1

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    return file_path



def file_to_buffer(file):
    file_binary_content = file.read()
    file_buffer = BytesIO(file_binary_content)
    return file_buffer

def get_image_embeddings(image):
    output = replicate.run(
        "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304",
        input={
            "input": image,
            "modality": "vision"
        }
    )

    return output

def get_text_embeddings(text):
    output = replicate.run(
        "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304",
        input={
            "text_input": text,
            "modality": "text"
        }
    )

    return output

def get_clothing_type(image):
    output = replicate.run(
        "yorickvp/llava-13b:b5f6212d032508382d61ff00469ddda3e32fd8a0e75dc39d8a4191bb742157fb",
        input={
            "image": image,
            "prompt": f"What is this piece of clothing? Please select one only: {CLOTHES_TYPES}"
        }
    )

    return "".join(output).lower()

def get_user_closet_length(query, collection):
    user_doc = collection.find_one(query)
    if user_doc:
        closet = user_doc.get('closet', {})
        return len(closet)
    
    raise ValueError("User not found")

def save_data_to_db(data:dict, db):
    collection = db.users
    query = {'username': data["username"]}
    new_item = {
        'path': data["image_path"],
        'type': data["type"],
        'embedding': data["image_embeddings"]
    }

    closet_length = get_user_closet_length(query, collection)
    new_item_key = f"item{closet_length + 1}"
    collection.update_one(
        {"username": data["username"]},
        {"$set": {f"closet.{new_item_key}": new_item}}
    )