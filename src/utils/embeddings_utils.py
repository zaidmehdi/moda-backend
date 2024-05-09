import replicate
import faiss
import numpy as np


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

    CLOTHES_TYPES = ["tops", "bottoms", "shoes", "outerwear"]

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