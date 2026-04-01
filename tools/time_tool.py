import httpx
from datetime import datetime
from zoneinfo import ZoneInfo
from core.tool import Tool


class TimeTool(Tool):
    @property
    def name(self) -> str:
        return "time_tool"

    @property
    def description(self) -> str:
        return "Get current local time for a city. Input: 'City Name'"

    def run(self, input_text: str = "") -> str:
        city = input_text.strip()
        if not city:
            return "Error: No city provided."

        print("Time tool started for city: " + city)

        try:
            # 1. Get coordinates
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_data = httpx.get(geo_url).json()

            if "results" not in geo_data:
                return f"Error: City '{city}' not found."

            loc = geo_data["results"][0]
            lat = loc["latitude"]
            lon = loc["longitude"]

            # 2. Get timezone from coordinates
            tz_url = f"https://timeapi.io/api/TimeZone/coordinate?latitude={lat}&longitude={lon}"
            tz_data = httpx.get(tz_url).json()

            timezone = tz_data["timeZone"]

            # 3. Use system clock with timezone
            now = datetime.now(ZoneInfo(timezone))

            return f"Current time in {city}: {now.strftime('%Y-%m-%d %H:%M:%S')}"

        except Exception as e:
            return f"System Error: {str(e)}"