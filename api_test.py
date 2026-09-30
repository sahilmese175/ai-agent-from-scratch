import requests

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 18.5204,
    "longitude": 73.8567,
    "current": "temperature_2m"
}

response = requests.get(url, params=params)

print("Status code:", response.status_code)

data = response.json()

temperature = data["current"]["temperature_2m"]

print("Current temperature:", temperature, "°C")