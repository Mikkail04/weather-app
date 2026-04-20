# from flask import Flask, render_template, request
# import requests
# import os
# from time import time

# app = Flask(__name__)

# # ---------------- CACHE ----------------
# cache = {}
# CACHE_DURATION = 600  # 10 minutes


# # ---------------- WEATHER HELPERS ----------------
# def get_weather_icon_and_desc(code):
#     if code == 0:
#         return "☀️", "Clear sky"
#     elif code == 1:
#         return "🌤", "Mainly clear"
#     elif code == 2:
#         return "⛅", "Partly cloudy"
#     elif code == 3:
#         return "☁️", "Overcast"
#     elif code in [45, 48]:
#         return "🌫", "Fog"
#     elif code == 51:
#         return "🌦", "Light drizzle"
#     elif code == 53:
#         return "🌦", "Moderate drizzle"
#     elif code == 55:
#         return "🌦", "Dense drizzle"
#     elif code == 61:
#         return "🌧", "Slight rain"
#     elif code == 63:
#         return "🌧", "Moderate rain"
#     elif code == 65:
#         return "🌧", "Heavy rain"
#     elif code == 71:
#         return "❄️", "Slight snow"
#     elif code == 73:
#         return "❄️", "Moderate snow"
#     elif code == 75:
#         return "❄️", "Heavy snow"
#     elif code == 95:
#         return "⛈", "Thunderstorm"
#     else:
#         return "🌍", "Unknown conditions"


# # ---------------- HOME ----------------
# @app.route("/")
# def home():
#     city = request.args.get("city", "Brooklyn")

#     # ---- GEOCODING ----
#     geo_res = requests.get(
#         "https://geocoding-api.open-meteo.com/v1/search",
#         params={"name": city, "count": 1}
#     ).json()

#     if not geo_res.get("results"):
#         return render_template("index.html", error="City not found")

#     lat = geo_res["results"][0]["latitude"]
#     lon = geo_res["results"][0]["longitude"]

#     cache_key = f"{lat},{lon}"
#     weather_res = None

#     # ---- CHECK CACHE ----
#     if cache_key in cache:
#         cached_data, timestamp = cache[cache_key]
#         if time() - timestamp < CACHE_DURATION:
#             weather_res = cached_data

#     # ---- FETCH FROM API IF NEEDED ----
#     if weather_res is None:
#         try:
#             weather_res = requests.get(
#                 "https://api.open-meteo.com/v1/forecast",
#                 params={
#                     "latitude": lat,
#                     "longitude": lon,
#                     "current_weather": True,
#                     "daily": "weathercode,temperature_2m_max,temperature_2m_min",
#                     "timezone": "auto"
#                 },
#                 timeout=5
#             ).json()

#             # Save only valid data
#             if not weather_res.get("error"):
#                 cache[cache_key] = (weather_res, time())

#         except:
#             weather_res = None

#     # ---- FALLBACK IF API FAILS ----
#     if not weather_res or weather_res.get("error"):
#         if cache_key in cache:
#             weather_res, _ = cache[cache_key]
#         else:
#             # 👇 HARD FALLBACK (always works)
#             return render_template(
#                 "index.html",
#                 city=city,
#                 temp_c=20,
#                 temp_f=68,
#                 wind=5,
#                 icon="🌤",
#                 description="Demo weather (API limit reached)",
#                 forecast=[]
#             )

#     # ---- CURRENT WEATHER ----
#     current = weather_res.get("current_weather")
#     if not current:
#         return render_template("index.html", error="Weather data missing")

#     temp_c = current["temperature"]
#     wind = current["windspeed"]
#     weathercode = current.get("weathercode", 0)

#     icon, description = get_weather_icon_and_desc(weathercode)
#     temp_f = (temp_c * 9/5) + 32

#     # ---- FORECAST ----
#     forecast = []
#     if "daily" in weather_res:
#         days = weather_res["daily"]["time"]
#         max_t = weather_res["daily"]["temperature_2m_max"]
#         min_t = weather_res["daily"]["temperature_2m_min"]
#         codes = weather_res["daily"]["weathercode"]

#         for i in range(len(days)):
#             icon_f, desc_f = get_weather_icon_and_desc(codes[i])

#             forecast.append({
#                 "date": days[i],
#                 "icon": icon_f,
#                 "desc": desc_f,
#                 "max": round((max_t[i] * 9/5) + 32, 1),
#                 "min": round((min_t[i] * 9/5) + 32, 1)
#             })

#     return render_template(
#         "index.html",
#         city=city,
#         temp_c=temp_c,
#         temp_f=round(temp_f, 1),
#         wind=wind,
#         icon=icon,
#         description=description,
#         forecast=forecast
#     )


# # ---------------- COORDS ----------------
# @app.route("/coords")
# def coords():
#     lat = request.args.get("lat", type=float)
#     lon = request.args.get("lon", type=float)

#     if not lat or not lon:
#         return render_template("index.html", error="Location not available")

#     cache_key = f"{lat},{lon}"
#     weather_res = None

#     # ---- CACHE ----
#     if cache_key in cache:
#         cached_data, timestamp = cache[cache_key]
#         if time() - timestamp < CACHE_DURATION:
#             weather_res = cached_data

#     # ---- API ----
#     if weather_res is None:
#         try:
#             weather_res = requests.get(
#                 "https://api.open-meteo.com/v1/forecast",
#                 params={
#                     "latitude": lat,
#                     "longitude": lon,
#                     "current_weather": True,
#                     "daily": "weathercode,temperature_2m_max,temperature_2m_min",
#                     "timezone": "auto"
#                 },
#                 timeout=5
#             ).json()

#             if not weather_res.get("error"):
#                 cache[cache_key] = (weather_res, time())

#         except:
#             weather_res = None

#     # ---- FALLBACK ----
#     if not weather_res or weather_res.get("error"):
#         if cache_key in cache:
#             weather_res, _ = cache[cache_key]
#         else:
#             return render_template(
#                 "index.html",
#                 city="Your Location",
#                 temp_c=20,
#                 temp_f=68,
#                 wind=5,
#                 icon="🌤",
#                 description="Demo weather (API limit reached)",
#                 forecast=[]
#             )

#     current = weather_res.get("current_weather")
#     if not current:
#         return render_template("index.html", error="Weather data missing")

#     temp_c = current["temperature"]
#     wind = current["windspeed"]
#     weathercode = current.get("weathercode", 0)

#     icon, description = get_weather_icon_and_desc(weathercode)
#     temp_f = (temp_c * 9/5) + 32

#     forecast = []
#     if "daily" in weather_res:
#         days = weather_res["daily"]["time"]
#         max_t = weather_res["daily"]["temperature_2m_max"]
#         min_t = weather_res["daily"]["temperature_2m_min"]
#         codes = weather_res["daily"]["weathercode"]

#         for i in range(len(days)):
#             icon_f, desc_f = get_weather_icon_and_desc(codes[i])

#             forecast.append({
#                 "date": days[i],
#                 "icon": icon_f,
#                 "desc": desc_f,
#                 "max": round((max_t[i] * 9/5) + 32, 1),
#                 "min": round((min_t[i] * 9/5) + 32, 1)
#             })

#     return render_template(
#         "index.html",
#         city="Your Location",
#         temp_c=temp_c,
#         temp_f=round(temp_f, 1),
#         wind=wind,
#         icon=icon,
#         description=description,
#         forecast=forecast
#     )


# # ---------------- RUN ----------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# Get API key from environment (Render)
API_KEY = os.environ.get("API_KEY")
print("API KEY LOADED:", bool(API_KEY))


# ---------------- HOME ----------------
@app.route("/")
def home():
    city = request.args.get("city", "New York")

    try:
        # -------- CURRENT WEATHER --------
        weather_res = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=5
        ).json()

        # -------- FORECAST (5-day / 3-hour intervals) --------
        forecast_res = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=5
        ).json()

    except:
        return render_template("index.html", error="API request failed")

    # -------- ERROR HANDLING --------
    if str(weather_res.get("cod")) != "200":
        print("ERROR:", weather_res)
        return render_template(
            "index.html",
            error=weather_res.get("message", "Weather API error")
        )

    # -------- CURRENT WEATHER --------
    temp_c = weather_res["main"]["temp"]
    wind = weather_res["wind"]["speed"]
    description = weather_res["weather"][0]["description"]
    icon_code = weather_res["weather"][0]["icon"]

    temp_f = (temp_c * 9/5) + 32
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    # -------- FORECAST PROCESSING --------
    forecast = []

    if forecast_res.get("cod") == "200":
        seen_dates = set()

        for item in forecast_res["list"]:
            date = item["dt_txt"].split(" ")[0]

            # Only take one entry per day (around noon)
            if "12:00:00" in item["dt_txt"] and date not in seen_dates:
                seen_dates.add(date)

                temp_max = item["main"]["temp_max"]
                temp_min = item["main"]["temp_min"]

                forecast.append({
                    "date": date,
                    "icon_url": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                    "desc": item["weather"][0]["description"].title(),
                    "max": round((temp_max * 9/5) + 32, 1),
                    "min": round((temp_min * 9/5) + 32, 1)
                })

    # -------- RENDER --------
    return render_template(
        "index.html",
        city=city,
        temp_c=temp_c,
        temp_f=round(temp_f, 1),
        wind=wind,
        description=description.title(),
        icon_url=icon_url,
        forecast=forecast   # ✅ THIS was missing before
    )


# ---------------- COORDS ----------------
@app.route("/coords")
def coords():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if not lat or not lon:
        return render_template("index.html", error="Location not available")

    try:
        weather_res = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=5
        ).json()
    except:
        return render_template("index.html", error="API request failed")

    if weather_res.get("cod") != 200:
        return render_template("index.html", error="Weather unavailable")

    temp_c = weather_res["main"]["temp"]
    wind = weather_res["wind"]["speed"]
    description = weather_res["weather"][0]["description"]
    icon_code = weather_res["weather"][0]["icon"]

    temp_f = (temp_c * 9/5) + 32
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    return render_template(
        "index.html",
        city="Your Location",
        temp_c=temp_c,
        temp_f=round(temp_f, 1),
        wind=wind,
        description=description.title(),
        icon_url=icon_url
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))