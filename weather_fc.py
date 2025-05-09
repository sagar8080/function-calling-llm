import os
import requests
import datetime
import re
import json
from openai import OpenAI
from dateparser import parse

MODEL = "gpt-4.1-mini-2025-04-14"

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
if not client.api_key:
    print("Error: The OpenAI API key is not set.")
    print("Please set the OPENAI_API_KEY environment variable or pass the api_key argument to the OpenAI client.")


def parse_date(text):
    """
    Parses a natural language date string into a datetime.date object.
    Supports expressions like 'today', 'tomorrow', 'next Monday', 'this weekend', 'in 3 days', etc.
    """
    if not text or not isinstance(text, str):
        return None

    text = text.strip().lower()
    today = datetime.date.today()
    if text in ["today", "now"]:
        return today
    if text == "tomorrow":
        return today + datetime.timedelta(days=1)
    if text == "this weekend":
        days_ahead = (5 - today.weekday()) % 7
        return today + datetime.timedelta(days=days_ahead)
    parsed = parse(text, settings={'PREFER_DATES_FROM': 'future'})
    if parsed:
        return parsed.date()
    return None

def get_weather(location, datetime_str=None):
    """
    Fetches current or forecasted weather for a given location and optional datetime
    using the Open-Meteo API. Returns a string summary or an error message.
    """
    if not location or not isinstance(location, str):
        return "Sorry, I couldn't determine the location for the weather query."

    # Geocoding to get latitude and longitude
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": location, "count": 1, "language": "en", "format": "json"}
    
    try:
        geo_resp = requests.get(geocode_url, params=geo_params)
        geo_resp.raise_for_status()  # Raise an exception for HTTP errors
        geo_data = geo_resp.json()
    except requests.exceptions.RequestException as e:
        return f"Sorry, there was an error contacting the geocoding service: {e}"
    except json.JSONDecodeError:
        return "Sorry, the geocoding service returned an invalid response."

    if not geo_data.get("results"):
        return f"Sorry, I couldn't find location data for '{location}'."

    try:
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        resolved_location = geo_data["results"][0]["name"]
    except (IndexError, KeyError):
        return f"Sorry, couldn't parse geocoding data for '{location}'."

    # Determine date for forecast
    if datetime_str:
        date_obj = parse_date(datetime_str)
        if not date_obj:
            return f"Sorry, I couldn't understand the date/time '{datetime_str}'."
        forecast_date_str = date_obj.strftime("%Y-%m-%d")
    else:
        # Default to today if no datetime_str is provided
        forecast_date_str = datetime.date.today().strftime("%Y-%m-%d")

    # Fetch weather forecast for the determined date
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "start_date": forecast_date_str,
        "end_date": forecast_date_str
    }
    
    try:
        weather_resp = requests.get(weather_url, params=weather_params)
        weather_resp.raise_for_status() # Raise an exception for HTTP errors
        weather_data = weather_resp.json()
    except requests.exceptions.RequestException as e:
        return f"Sorry, there was an error retrieving the weather data: {e}"
    except json.JSONDecodeError:
        return "Sorry, the weather service returned an invalid response."

    try:
        # Extract daily weather data (API returns lists even for single day)
        temps_max = weather_data["daily"]["temperature_2m_max"][0]
        temps_min = weather_data["daily"]["temperature_2m_min"][0]
        precipitation = weather_data["daily"]["precipitation_sum"][0]
        actual_forecast_date = weather_data["daily"]["time"][0] # The date returned by the API
    except (KeyError, IndexError, TypeError):
        return f"Sorry, weather data is incomplete or unavailable for {resolved_location} on {forecast_date_str}."

    # Build summary string
    summary = (
        f"Weather for {resolved_location} on {actual_forecast_date}:\n"
        f"- Max temperature: {temps_max}°C\n"
        f"- Min temperature: {temps_min}°C\n"
        f"- Precipitation: {precipitation} mm"
    )
    return summary

# --- OpenAI Function Calling Schema ---
weather_function_schema = {
    "name": "get_weather",
    "description": "Get the current weather or forecast for a specific location and optional date.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state/country, e.g., San Francisco, CA or Paris, France"
            },
            "datetime_str": {
                "type": "string",
                "description": "Optional. A date or natural language time reference like 'tomorrow', 'next Monday', or '2024-07-15'. If omitted, current weather or today's forecast is assumed."
            }
        },
        "required": ["location"]
    }
}

def openai_chat(user_message, model_name=MODEL):
    """
    Handles user input, determines if a weather query is made,
    calls the get_weather function via OpenAI tool use, and returns the assistant's response.
    """
    if not client.api_key: # Check again in case it wasn't set and script continued
        return "OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."

    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant. "
            "If the user asks about the weather, you must use the 'get_weather' function "
            "to find the weather information. Provide the location and optionally a date string. "
            "If the user does not ask about weather, respond normally."
        )},
        {"role": "user", "content": user_message}
    ]

    try:
        # First API call to OpenAI
        response = client.chat.completions.create(
            model=model_name, # Or any other model that supports tool use
            messages=messages,
            tools=[{"type": "function", "function": weather_function_schema}],
            tool_choice="auto" # "auto" lets the model decide; or {"type": "function", "function": {"name": "get_weather"}}
        )
        response_message = response.choices[0].message

        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message)
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            
            if function_name == "get_weather":
                function_args_str = tool_call.function.arguments
                try:
                    function_args = json.loads(function_args_str)
                except json.JSONDecodeError:
                    function_response = "Error: Invalid arguments received for weather function."
                else:
                    location = function_args.get("location")
                    datetime_str = function_args.get("datetime_str") # This can be None
                    function_response = get_weather(location=location, datetime_str=datetime_str)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

                # Second API call to OpenAI with the function's result
                second_response = client.chat.completions.create(
                    model=model_name,
                    messages=messages
                )
                return second_response.choices[0].message.content
            else:
                # Fallback if a different, unexpected function is called
                return "Assistant decided to call an unknown or unhandled function."
        else:
            # No tool call was made, return the assistant's direct response
            return response_message.content

    except Exception as e: # Catch potential OpenAI API errors or other issues
        return f"An error occurred: {e}"


if __name__ == "__main__":
    print("Weather Assistant Demo")
    print("Ensure your OPENAI_API_KEY environment variable is set.")
    print("Type your query (or 'quit' to exit):")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        if not user_input:
            continue
            
        assistant_reply = openai_chat(user_input)
        print(f"Assistant: {assistant_reply}")
