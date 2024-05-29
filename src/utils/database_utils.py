import io
import os

from PIL import Image
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """Checks if uploaded file is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, no_background_file):
    """Makes filename unique and saves it"""
    filename = secure_filename(file.filename)
    name, _ = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(os.getenv("UPLOAD_FOLDER"), filename)):
        filename = f"{name}_{counter}.png"
        counter += 1

    file_path = os.path.join(os.getenv("UPLOAD_FOLDER"), filename)

    no_background_image = Image.open(io.BytesIO(no_background_file))
    img_io = io.BytesIO()
    no_background_image.save(img_io, format='PNG')
    img_io.seek(0)
    with open(file_path, 'wb') as f:
        f.write(img_io.getbuffer())

    return file_path


def get_user_closet_length(query, collection):
    user_doc = collection.find_one(query)
    if user_doc:
        closet = user_doc.get('closet', {})
        return len(closet)
    
    raise ValueError("User not found")

def save_data_to_db(data:dict, db):
    collection = db.users
    query = {'_id': data["username"]}
    new_item = {
        'path': data["image_path"],
        'type': data["type"],
        'embedding': data["image_embeddings"]
    }

    closet_length = get_user_closet_length(query, collection)
    new_item_key = f"item{closet_length + 1}"
    collection.update_one(
        {"_id": data["username"]},
        {"$set": {f"closet.{new_item_key}": new_item}}
    )


