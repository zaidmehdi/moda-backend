import os

import replicate
from io import BytesIO
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
    file.save()

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

def save_image_to_db():
    return 