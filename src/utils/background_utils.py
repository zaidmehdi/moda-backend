from rembg import remove 
from PIL import Image 

def remove_image_background(file):
    # Removing the background from the given Image 
    output = remove(file) 
    return output