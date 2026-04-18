from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

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


# ---------------- HOME PAGE ----------------
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

    # safety check
    if "current_weather" not in weather_res:
        return render_template("index.html", error="Weather data unavailable")

    current = weather_res["current_weather"]

    temp_c = current["temperature"]
    wind = current["windspeed"]
    weathercode = current["weathercode"]

    icon, description = get_weather_icon_and_desc(weathercode)
    temp_f = (temp_c * 9/5) + 32

    # forecast
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


# ---------------- COORDS ----------------
@app.route("/coords")
def coords():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if not lat or not lon:
        return render_template("index.html", error="Location not available")

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

    if "current_weather" not in weather_res:
        return render_template("index.html", error="Weather data unavailable")

    current = weather_res["current_weather"]

    temp_c = current["temperature"]
    wind = current["windspeed"]
    weathercode = current["weathercode"]

    icon, description = get_weather_icon_and_desc(weathercode)
    temp_f = (temp_c * 9/5) + 32

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
                "max": round((max_t[i] * 9/5) + 32, 1),
                "min": round((min_t[i] * 9/5) + 32, 1),
                "icon": icon_f,
                "desc": desc_f
            })

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