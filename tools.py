import requests


def calculator(a, b, operation):

    a = float(a)
    b = float(b)

    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":
        return a / b

    else:
        return "Unknown operation"


def get_name():
    return "Sahil"


def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return "Unable to get weather data."

    data = response.json()

    temperature = data["current"]["temperature_2m"]

    return f"Current temperature is {temperature} °C"

def get_location(city):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return "Unable to find location."

    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        return "Location not found."

    location = data["results"][0]

    return {
        "name": location["name"],
        "latitude": location["latitude"],
        "longitude": location["longitude"]
    }