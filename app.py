from flask import Flask, render_template, request
import requests
import os
from datetime import datetime

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
            params={"q": city, "appid": API_KEY, "units": "metric"},
            timeout=5,
        ).json()

        # -------- FORECAST (5-day / 3-hour intervals) --------
        forecast_res = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"q": city, "appid": API_KEY, "units": "metric"},
            timeout=5,
        ).json()

    except:
        return render_template("index.html", error="API request failed")

    # -------- ERROR HANDLING --------
    if str(weather_res.get("cod")) != "200":
        print("ERROR:", weather_res)
        return render_template(
            "index.html", error=weather_res.get("message", "Weather API error")
        )

    # -------- CURRENT WEATHER --------
    temp_c = weather_res["main"]["temp"]
    wind = weather_res["wind"]["speed"]
    description = weather_res["weather"][0]["description"]
    icon_code = weather_res["weather"][0]["icon"]

    temp_f = (temp_c * 9 / 5) + 32
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    # -------- FORECAST PROCESSING --------
    forecast = []

    if forecast_res.get("cod") == "200":
        seen_dates = set()

        for item in forecast_res["list"]:
            raw_date = item["dt_txt"].split(" ")[0]
            date_obj = datetime.strptime(raw_date, "%Y-%m-%d")
            date = date_obj.strftime("%a")

            # Only take one entry per day (around noon)
            if "12:00:00" in item["dt_txt"] and date not in seen_dates:
                seen_dates.add(date)

                temp_max = item["main"]["temp_max"]
                temp_min = item["main"]["temp_min"]

                forecast.append(
                    {
                        "date": date,
                        "icon_url": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                        "desc": item["weather"][0]["description"].title(),
                        "max": round((temp_max * 9 / 5) + 32, 1),
                        "min": round((temp_min * 9 / 5) + 32, 1),
                    }
                )

    # -------- RENDER --------
    return render_template(
        "index.html",
        city=city,
        temp_c=temp_c,
        temp_f=round(temp_f, 1),
        wind=wind,
        description=description.title(),
        icon_url=icon_url,
        forecast=forecast,  # ✅ THIS was missing before
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
            params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"},
            timeout=5,
        ).json()
    except:
        return render_template("index.html", error="API request failed")

    if weather_res.get("cod") != 200:
        return render_template("index.html", error="Weather unavailable")

    temp_c = weather_res["main"]["temp"]
    wind = weather_res["wind"]["speed"]
    description = weather_res["weather"][0]["description"]
    icon_code = weather_res["weather"][0]["icon"]

    temp_f = (temp_c * 9 / 5) + 32
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    return render_template(
        "index.html",
        city="Your Location",
        temp_c=temp_c,
        temp_f=round(temp_f, 1),
        wind=wind,
        description=description.title(),
        icon_url=icon_url,
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
