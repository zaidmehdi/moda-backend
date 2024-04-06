import replicate
from io import BytesIO


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_image_description(image):
    input = {
    "image": image,
    "prompt": """Describe this piece of clothes with as many details as possible. 
                Your goal is to make it possible for a human to imagine the clothes 
                in the picture as faithfully as possible without seeing it."""
    }
    
    output = replicate.run(
    "yorickvp/llava-13b:b5f6212d032508382d61ff00469ddda3e32fd8a0e75dc39d8a4191bb742157fb",
    input=input
    )

    return "".join(output)


def image_to_buffer(image):
    file_binary_content = image.read()
    file_buffer = BytesIO(file_binary_content)
    return file_buffer