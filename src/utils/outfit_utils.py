from utils.embeddings_utils import get_text_embeddings, get_items_by_type, get_items_embeddings, get_most_similar_embedding


def prompt_gpt(client, history, prompt):
    history.append(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= history
    )
    content = response.choices[0].message.content
    history.append({"role": "assistant", "content": content})

    return content[15:], history


def get_tops(client, history, gender, context, temperature):
    prompt = {"role": "user", "content": f"-Context: `{context}`,\n-Gender: `{gender}`\
              \n-Temperature: `{temperature}` degrees celsius.\
              \nGiven this context, generate a description for what I should wear as a top:"}
    
    return prompt_gpt(client, history, prompt)


def get_bottoms(client, history):
    prompt = {"role": "user", "content": f"Given the previous answers, generate a description for what \
              I should wear as a bottom:"}
    
    return prompt_gpt(client, history, prompt)


def get_shoes(client, history):
    prompt = {"role": "user", "content": f"Given the previous answers, generate a description for what \
              I should wear as shoes:"}
    
    return prompt_gpt(client, history, prompt)


def get_outerwear(client, history, temperature):
    prompt = {"role": "user", "content": f"Given the previous answers, and given the temperature, \
              generate a description for what I should wear as outwear. If the temperature I gave you \
              ({temperature}) is above 25, write none."}
    
    content, history = prompt_gpt(client, history, prompt)
    if "none" in content.lower():
        return None
    
    return content[15:]


def get_outfit_description(client, gender, context, temperature):
    """given some context, returns a dictionary describing what you should wear in your outfit."""

    outfit_description = {}

    history = [{"role": "system", "content": "You are a fashion expert who is dedicated to picking outfits for a user. \
                You will receive context from the user that will help you choose an outfit. \
                An outfit contains four items: top, bottom, shoes, outwear. \
                The outwear is optional and depends on the weather, if it is not needed, \
                only write `none` and nothing else. You will need to provide a description for each item one by one.\
                I want the description to include: color, style, fit, and material. Make sure the different items \
                go well toghether in terms of style, color and other factors. the answer should be in this format: \
                'description': "}]
    
    outfit_description["tops"], history = get_tops(client, history, gender, context, temperature)
    outfit_description["bottoms"], history = get_bottoms(client, history)
    outfit_description["shoes"] = get_shoes(client, history)

    outerwear = get_outerwear(client, history, temperature)
    if outerwear:
        outfit_description["outerwear"] = outerwear

    return outfit_description


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