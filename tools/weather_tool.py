import httpx
from core.tool import Tool


class WeatherTool(Tool):
    @property
    def name(self) -> str:
        return "weather_tool"

    @property
    def description(self) -> str:
        return "Get current weather for a city."

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name"
                }
            },
            "required": ["city"]
        }

    def run(self, params) -> str:
        city = params.get("city")
        if not city:
            return "Error: 'city' parameter is required."

        try:
            # 1. Geocoding (City -> Lat/Lon)
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_data = httpx.get(geo_url, params={"name": city, "count": 1}).json()

            if "results" not in geo_data:
                return f"Error: City '{city}' not found."

            loc = geo_data["results"][0]
            lat, lon = loc["latitude"], loc["longitude"]

            # 2. Weather (Lat/Lon -> Forecast)
            weather_url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "timezone": "auto"
            }

            w_resp = httpx.get(weather_url, params=params).json()
            curr = w_resp["current_weather"]

            return (
                f"Weather in {city}: "
                f"{curr['temperature']}°C, "
                f"Windspeed: {curr['windspeed']} km/h."
            )

        except Exception as e:
            return f"System Error: {str(e)}"