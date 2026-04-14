# Import Flask class (main app), render_template (for HTML), and request (for URL params)
from flask import Flask, render_template, request

# Import requests to make API calls
import requests
import os

# Create the Flask app instance
app = Flask(__name__)

# Get a weather icon and description based on weather conditions
def get_weather_icon_and_desc(code):
    if code == 0:
        return "☀️", "Clear sky"
    elif code in [1]:
        return "🌤", "Mainly clear"
    elif code in [2]:
        return "⛅", "Partly cloudy"
    elif code in [3]:
        return "☁️", "Overcast"
    elif code in [45, 48]:
        return "🌫", "Fog"
    elif code in [51]:
        return "🌦", "Light drizzle"
    elif code in [53]:
        return "🌦", "Moderate drizzle"
    elif code in [55]:
        return "🌦", "Dense drizzle"
    elif code in [61]:
        return "🌧", "Slight rain"
    elif code in [63]:
        return "🌧", "Moderate rain"
    elif code in [65]:
        return "🌧", "Heavy rain"
    elif code in [71]:
        return "❄️", "Slight snow"
    elif code in [73]:
        return "❄️", "Moderate snow"
    elif code in [75]:
        return "❄️", "Heavy snow"
    elif code in [95]:
        return "⛈", "Thunderstorm"
    else:
        return "🌍", "Unknown conditions"

# Define route for homepage ("/")
@app.route("/")
def home():
    # Get 'city' from URL (e.g. ?city=London), default to "Brooklyn" if not provided
    city = request.args.get("city", "Brooklyn")

    # URL for Open-Meteo geocoding API (converts city name → coordinates)
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    # Send GET request with city name, limit results to 1, convert response to JSON
    geo_res = requests.get(geo_url, params={"name": city, "count": 1}).json()

    # If API didn't return results, show error message on page
    if "results" not in geo_res:
        return render_template("index.html", error="City not found")

    # Extract latitude from API response
    lat = geo_res["results"][0]["latitude"]

    # Extract longitude from API response
    lon = geo_res["results"][0]["longitude"]

    # Send request to weather API using coordinates
    weather_res = requests.get("https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,              # latitude of city
            "longitude": lon,             # longitude of city
            "current_weather": True,      # request current weather only
            "daily": "weathercode,temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }
    ).json()  # convert response to JSON
    
    # Get forecast information
    forecast_days = weather_res["daily"]["time"]
    forecast_max = weather_res["daily"]["temperature_2m_max"]
    forecast_min = weather_res["daily"]["temperature_2m_min"]
    forecast_codes = weather_res["daily"]["weathercode"]
    forecast = []

    for i in range(len(forecast_days)):
        icon, desc = get_weather_icon_and_desc(forecast_codes[i])
        max_c = forecast_max[i]
        min_c = forecast_min[i]

        # Convert to Fahrenheit
        max_f = (max_c * 9/5) + 32
        min_f = (min_c * 9/5) + 32

        forecast.append({
            "date": forecast_days[i],
            "max": round(max_f, 1),
            "min": round(min_f, 1),
            "icon": icon,
            "desc": desc
        })

    # Get temperature in Celsius from response
    temp_c = weather_res["current_weather"]["temperature"]
    
    # Get an icon and description that represents the weather
    weathercode = weather_res["current_weather"]["weathercode"]
    icon, description = get_weather_icon_and_desc(weathercode)

    # Convert Celsius to Fahrenheit
    temp_f = (temp_c * 9/5) + 32

    # Get wind speed from response
    wind = weather_res["current_weather"]["windspeed"]

    # Render HTML template and pass values to it
    return render_template(
        "index.html",
        city=city,                    # city name
        temp_c=temp_c,                # temperature in Celsius
        temp_f=round(temp_f, 1),      # temperature in Fahrenheit (rounded)
        wind=wind,                    # wind speed
        icon=icon,                    # weather icon
        description=description,      # description
        forecast=forecast
    )

# Only run the app if this file is executed directly (not imported)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    

# Route for handling GPS coordinates from browser
@app.route("/coords")
def coords():
    # Get latitude from URL (?lat=...)
    lat = request.args.get("lat")

    # Get longitude from URL (?lon=...)
    lon = request.args.get("lon")

    # Call weather API using provided coordinates
    weather_res = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,           # user's latitude
            "longitude": lon,          # user's longitude
            "current_weather": True,  # request current weather
            "daily": "weathercode,temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }
    ).json()  # convert response to JSON
    
    # Get forecast information
    forecast_days = weather_res["daily"]["time"]
    forecast_max = weather_res["daily"]["temperature_2m_max"]
    forecast_min = weather_res["daily"]["temperature_2m_min"]
    forecast_codes = weather_res["daily"]["weathercode"]
    forecast = []

    for i in range(len(forecast_days)):
        icon, desc = get_weather_icon_and_desc(forecast_codes[i])
        max_c = forecast_max[i]
        min_c = forecast_min[i]

        # Convert to Fahrenheit
        max_f = (max_c * 9/5) + 32
        min_f = (min_c * 9/5) + 32

        forecast.append({
            "date": forecast_days[i],
            "max": round(max_f, 1),
            "min": round(min_f, 1),
            "icon": icon,
            "desc": desc
        })

    # Extract temperature in Celsius
    temp_c = weather_res["current_weather"]["temperature"]
    
    # Get an icon and description that represents the weather
    weathercode = weather_res["current_weather"]["weathercode"]
    icon, description = get_weather_icon_and_desc(weathercode)

    # Convert to Fahrenheit
    temp_f = (temp_c * 9/5) + 32

    # Extract wind speed
    wind = weather_res["current_weather"]["windspeed"]

    # Render same HTML but label as "Your Location"
    return render_template(
        "index.html",
        city="Your Location",         # label instead of city name
        temp_c=temp_c,
        temp_f=round(temp_f, 1),
        wind=wind,
        icon=icon,
        description=description,
        forecast=forecast
    )
    