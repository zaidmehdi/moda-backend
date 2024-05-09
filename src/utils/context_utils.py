import os
import requests

from dotenv import load_dotenv
from geopy.geocoders import Nominatim


load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


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
