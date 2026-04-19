# Added in order to implement expiration
from time import time
cache = {}
CACHE_DURATION = 600  # 10 minutes

from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)


# ---------------- WEATHER HELPERS ----------------
def get_weather_icon_and_desc(code):
    if code == 0:
        return "☀️", "Clear sky"
    elif code == 1:
        return "🌤", "Mainly clear"
    elif code == 2:
        return "⛅", "Partly cloudy"
    elif code == 3:
        return "☁️", "Overcast"
    elif code in [45, 48]:
        return "🌫", "Fog"
    elif code == 51:
        return "🌦", "Light drizzle"
    elif code == 53:
        return "🌦", "Moderate drizzle"
    elif code == 55:
        return "🌦", "Dense drizzle"
    elif code == 61:
        return "🌧", "Slight rain"
    elif code == 63:
        return "🌧", "Moderate rain"
    elif code == 65:
        return "🌧", "Heavy rain"
    elif code == 71:
        return "❄️", "Slight snow"
    elif code == 73:
        return "❄️", "Moderate snow"
    elif code == 75:
        return "❄️", "Heavy snow"
    elif code == 95:
        return "⛈", "Thunderstorm"
    else:
        return "🌍", "Unknown conditions"


# ---------------- HOME ----------------
@app.route("/")
def home():
    city = request.args.get("city", "Brooklyn")

    geo_res = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1}
    ).json()

    if not geo_res.get("results"):
        return render_template("index.html", error="City not found")

    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]

    cache_key = f"{lat},{lon}"

    # Check cache
    if cache_key in cache:
        cached_data, timestamp = cache[cache_key]
        if time() - timestamp < CACHE_DURATION:
            weather_res = cached_data
        else:
            weather_res = None
    else:
        weather_res = None

    # If no valid cache → call API
    if weather_res is None:
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
     
    # Save to cache
    cache[cache_key] = (weather_res, time())    

    # ✅ FIXED CHECK (correct key)
    if weather_res.get("error"):
        return render_template("index.html", error=weather_res.get("reason"))
    current = weather_res.get("current_weather")

    if not current:
        print(weather_res)  # debugging
        return render_template("index.html", error="Weather data unavailable")

    # ---------------- CURRENT WEATHER ----------------
    temp_c = current["temperature"]
    wind = current["windspeed"]
    weathercode = current.get("weathercode", 0)

    icon, description = get_weather_icon_and_desc(weathercode)
    temp_f = (temp_c * 9/5) + 32

    # ---------------- FORECAST ----------------
    forecast = []
    if "daily" in weather_res:
        days = weather_res["daily"]["time"]
        max_t = weather_res["daily"]["temperature_2m_max"]
        min_t = weather_res["daily"]["temperature_2m_min"]
        codes = weather_res["daily"]["weathercode"]

        for i in range(len(days)):
            icon_f, desc_f = get_weather_icon_and_desc(codes[i])

            forecast.append({
                "date": days[i],
                "icon": icon_f,
                "desc": desc_f,
                "max": round((max_t[i] * 9/5) + 32, 1),
                "min": round((min_t[i] * 9/5) + 32, 1)
            })

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


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))