from rembg import remove 


def remove_image_background(file):
    # Removing the background from the given Image 

    input_image = file.read()
    output = remove(input_image) 
    return output