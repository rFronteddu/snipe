import httpx
from core.tool import Tool


class WeatherTool(Tool):
    @property
    def name(self) -> str:
        return "weather_tool"

    @property
    def description(self) -> str:
        return "Get current weather for a city. Input: 'City Name'"

    def run(self, input_text: str = "") -> str:
        city = input_text.strip()
        if not city:
            return "Error: No city provided."

        try:
            # 1. Geocoding (City -> Lat/Lon)
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_data = httpx.get(geo_url).json()

            if "results" not in geo_data:
                return f"Error: City '{city}' not found."

            loc = geo_data["results"][0]
            lat, lon = loc["latitude"], loc["longitude"]

            # 2. Weather (Lat/Lon -> Forecast)
            weather_url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat, "longitude": lon,
                "current_weather": "true", "timezone": "auto"
            }
            w_resp = httpx.get(weather_url, params=params).json()
            curr = w_resp["current_weather"]

            return f"Weather in {city}: {curr['temperature']}°C, Windspeed: {curr['windspeed']}km/h."

        except Exception as e:
            return f"System Error: {str(e)}"