import requests
import os

import faiss
import numpy as np
import replicate
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from werkzeug.utils import secure_filename


CLOTHES_TYPES = ["tops", "bottoms", "shoes", "outerwear"]
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


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
        "yorickvp/llava-v1.6-34b:41ecfbfb261e6c1adf3ad896c9066ca98346996d7c4045c5bc944a79d430f174",
        input={
            "image": image,
            "prompt": f"What is this piece of clothing? Please select ONLY ONE CHOICE: {CLOTHES_TYPES}. \
                If you are in doubt, just pick ONE OF THEM.\
                \nIf you think it's outerwear but it doesn't have a zipper or buttons, it should \
                be considered as: 'tops'. Keep in mind that you shouldn't write anything except one \
                of the 4 choices, and no other text."
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



def get_city_from_coord(latitude, longitude):
    geolocator = Nominatim(user_agent="city_name_app")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    address = location.address if location else None
    if address:
        city = address.split(",")[-3]
        return city.strip()

    return None

def fetch_weather(latitude, longitude):
    city_name = get_city_from_coord(latitude, longitude)
    if not city_name:
        return None
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    return data["main"]["feels_like"]

def get_gender_by_username(username:str, db):
    collection = db.users
    document = collection.find_one({"_id": username})
    if not document:
        return None
    
    return document.get("gender")


def prompt_gpt(client, gender, context, temperature):
    """given some context, returns a dictionary describing what you should wear in your outfit."""
    outfit = {"tops": "",
              "bottoms": "",
              "shoes": "",
              "outerwear": ""}

    history = [{"role": "system", "content": "You are a fashion expert who is dedicated to picking outfits for a user. \
                You will receive context from the user that will help you choose an outfit. \
                An outfit contains four items: top, bottom, shoes, outwear. \
                The outwear is optional and depends on the weather, if it is not needed, \
                only write `none` and nothing else. You will need to provide a description for each item one by one.\
                I want the description to include: color, style, fit, and material. Make sure the different items \
                go well toghether in terms of style, color and other factors. the answer should be in this format: \
                'description': "}]
    
    prompt = {"role": "user", "content": f"-Context: `{context}`,\n-Gender: `{gender}`\
              \n-Temperature: `{temperature}` degrees celsius.\
              \nGiven this context, generate a description for what I should wear as a top:"}
    
    history.append(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= history
    )
    content = response.choices[0].message.content
    history.append({"role": "assistant", "content": content})
    outfit["tops"] = content[13:]


    prompt = {"role": "user", "content": f"Given the previous answers, generate a description for what \
              I should wear as a bottom:"}
    
    history.append(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= history
    )
    content = response.choices[0].message.content
    history.append({"role": "assistant", "content": content})
    outfit["bottoms"] = content[13:]


    prompt = {"role": "user", "content": f"Given the previous answers, generate a description for what \
              I should wear as shoes:"}
    
    history.append(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= history
    )
    content = response.choices[0].message.content
    history.append({"role": "assistant", "content": content})
    outfit["shoes"] = content[13:]


    prompt = {"role": "user", "content": f"Given the previous answers, generate a description for what \
              I should wear as outwear (remember to write 'none' if i shouldn't wear any):"}
    
    history.append(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= history
    )
    content = response.choices[0].message.content
    history.append({"role": "assistant", "content": content})
    if content.lower() == "none":
        outfit["outerwear"] = None
    else:
        outfit["outerwear"] = content[13:]

    return outfit


def get_items_by_type(db, username, item_type:str):
    collection = db.users
    document = collection.find_one({"_id": username})
    if not document:
        return None
    closet = document.get("closet", {})
    items = [closet[key] for key in closet if closet[key].get("type") == item_type]

    return items

def get_items_embeddings(items):
    embeddings = []
    for item in items:
        embedding = item.get("embedding")
        embeddings.append(embedding)

    return embeddings

def get_most_similar_embedding(embedding, embeddings_list):
    embedding = np.asarray(embedding, dtype=np.float32)
    embeddings_list = np.asarray(embeddings_list, dtype=np.float32)

    d = embedding.shape[0]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings_list)
    _, most_similar_index = index.search(np.expand_dims(embedding, axis=0), 1)

    return most_similar_index[0][0]

def get_outfit(outfit_description, username, db):
    outfit = []

    for item_type, description in outfit_description.items():
        description_embedding = get_text_embeddings(description)

        items = get_items_by_type(db, username, item_type)
        items_embeddings= get_items_embeddings(items)
        outfit_item_index = get_most_similar_embedding(description_embedding, items_embeddings)
        outfit_item_path = items[outfit_item_index]["path"]
        if item_type == "outerwear":
            outfit.insert(0, outfit_item_path)
        else:
            outfit.append(outfit_item_path)

    return outfit