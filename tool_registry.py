from tools import calculator, get_name, get_weather, get_location

TOOLS = {

    "calculator": {
        "function": calculator,
        "description": "Performs mathematical calculations.",
        "arguments": {
            "a": "first number",
            "b": "second number",
            "operation": "add, subtract, multiply, or divide"
        }
    },

    "get_name": {
        "function": get_name,
        "description": "Returns the user's name.",
        "arguments": {}
    },

    "get_weather": {
        "function": get_weather,
        "description": "Gets the current temperature for a location using latitude and longitude.",
        "arguments": {
            "latitude": "latitude of the location",
            "longitude": "longitude of the location"
        }
    },
    
    "get_location": {
    "function": get_location,
    "description": "Finds the latitude and longitude of a city.",
    "arguments": {
        "city": "name of the city"
    }
}
}