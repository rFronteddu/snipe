import httpx
from datetime import datetime
from zoneinfo import ZoneInfo
from core.tool import Tool

# todo extract geocode logic in core/utils/geocode.py

class TimeTool(Tool):

    @property
    def name(self) -> str:
        return "time_tool"

    @property
    def description(self) -> str:
        return "Get current local time for a city."

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
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_data = httpx.get(
                geo_url,
                params={"name": city, "count": 1},
                timeout=10.0
            ).json()

            if "results" not in geo_data:
                return f"Error: City '{city}' not found."

            loc = geo_data["results"][0]

            lat = loc["latitude"]
            lon = loc["longitude"]
            timezone = loc.get("timezone")
            if not timezone:
                timezone = "UTC"
            now = datetime.now(ZoneInfo(timezone))
            return f"Current time in {city}: {now.strftime('%Y-%m-%d %H:%M:%S')}"

        except Exception as e:
            print(e)
            return f"System Error: {str(e)}"