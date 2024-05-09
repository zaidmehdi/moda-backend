import os

from werkzeug.utils import secure_filename


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


