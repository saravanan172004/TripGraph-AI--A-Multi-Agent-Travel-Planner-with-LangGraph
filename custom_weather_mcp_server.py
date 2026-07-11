from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv


load_dotenv()


# FIX #1: this was `FASTMCP(...)` — the class is `FastMCP`, so this was a
# NameError that crashed the whole script on startup, before any tool could
# even be registered. That's why get_tools() failed for EVERY server, not
# just weather.
mcp = FastMCP("Weather MCP Server")


OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# FIX #2: this was missing the @mcp.tool() decorator, so even once the
# server started, this function was never exposed as a callable MCP tool —
# weather_mcp_search() looks up a tool literally named "get_current_weather".
@mcp.tool()
def get_current_weather(city: str):

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            # FIX #3: OpenWeatherMap expects "metric", not "metrics".
            "units": "metric"
        }
    )

    data = response.json()

    if response.status_code != 200:
        return {
            "error": data.get("message", "Unable to fetch current weather")
        }

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }


@mcp.tool()
def get_forecast(city: str):

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        # FIX #3 (again): "metric", not "metrics".
        "units": "metric"
    }

    response = requests.get(
        url,
        params=params
    )

    # FIX #4: this was `requests.json()` — `requests` is the module, it has
    # no .json() method. Needed the response object instead.
    data = response.json()

    if response.status_code != 200:
        return {
            "error": data.get("message", "Unable to fetch forecast")
        }

    forecast = []

    for item in data["list"][:5]:
        forecast.append(
            {
                "datetime": item["dt_txt"],
                # FIX #5: this was `item["main"["temp"]]` — indexing the
                # string "main" with "temp" instead of chaining two lookups.
                "temperature": item["main"]["temp"],
                "weather": item["weather"][0]["description"]
            }
        )

    return {
        "city": city,
        "forecast": forecast
    }


if __name__ == "__main__":
    mcp.run()