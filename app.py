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


@app.route("/")
def home():
    city = request.args.get("city", "Brooklyn")

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_res = requests.get(geo_url, params={"name": city, "count": 1}).json()

    if "results" not in geo_res:
        return render_template("index.html", error="City not found")

    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]

    # ✅ FIXED API CALL
    weather_res = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "daily": "weathercode,temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }
    ).json()

    # ✅ FIXED SAFETY CHECK
    if "current_weather" not in weather_res:
        return render_template("index.html", error="Weather data unavailable")

    # Forecast
    forecast = []

    if "daily" in weather_res:
        forecast_days = weather_res["daily"]["time"]
        forecast_max = weather_res["daily"]["temperature_2m_max"]
        forecast_min = weather_res["daily"]["temperature_2m_min"]
        forecast_codes = weather_res["daily"]["weathercode"]

        for i in range(len(forecast_days)):
            icon, desc = get_weather_icon_and_desc(forecast_codes[i])

            max_f = (forecast_max[i] * 9/5) + 32
            min_f = (forecast_min[i] * 9/5) + 32

            forecast.append({
                "date": forecast_days[i],
                "icon": icon,
                "desc": desc,
                "max": round(max_f, 1),
                "min": round(min_f, 1)
            })

    # ✅ FIXED DATA ACCESS
    temp_c = weather_res["current_weather"]["temperature"]
    wind = weather_res["current_weather"]["windspeed"]
    weathercode = weather_res["current_weather"]["weathercode"]

    icon, description = get_weather_icon_and_desc(weathercode)
    temp_f = (temp_c * 9/5) + 32

    return render_template(
        "index.html",
        city=city,
        temp_c=temp_c,
        temp_f=round(temp_f, 1),
        wind=wind,
        icon=icon,
        description=description,
        forecast=forecast
    )


@app.route("/coords")
def coords():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    # ✅ FIXED API CALL
    weather_res = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "daily": "weathercode,temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }
    ).json()

    # ✅ SAFETY CHECK
    if "current" not in weather_res:
        return render_template("index.html", error="Weather data unavailable")

    forecast = []

    if "daily" in weather_res:
        forecast_days = weather_res["daily"]["time"]
        forecast_max = weather_res["daily"]["temperature_2m_max"]
        forecast_min = weather_res["daily"]["temperature_2m_min"]
        forecast_codes = weather_res["daily"]["weathercode"]

        for i in range(len(forecast_days)):
            icon, desc = get_weather_icon_and_desc(forecast_codes[i])

            max_f = (forecast_max[i] * 9/5) + 32
            min_f = (forecast_min[i] * 9/5) + 32

            forecast.append({
                "date": forecast_days[i],
                "max": round(max_f, 1),
                "min": round(min_f, 1),
                "icon": icon,
                "desc": desc
            })

    temp_c = weather_res["current_weather"]["temperature_2m"]
    wind = weather_res["current_weather"]["windspeed"]
    weathercode = weather_res["current_weather"]["weathercode"]

    icon, description = get_weather_icon_and_desc(weathercode)
    temp_f = (temp_c * 9/5) + 32

    return render_template(
        "index.html",
        city="Your Location",
        temp_c=temp_c,
        temp_f=round(temp_f, 1),
        wind=wind,
        icon=icon,
        description=description,
        forecast=forecast
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))