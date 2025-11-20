# weather_service.py
"""Weather API service layer using httpx (async)."""

from typing import Dict
import httpx
from config import Config

class WeatherServiceError(Exception):
    pass

class WeatherService:
    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL
        self.timeout = Config.TIMEOUT

    async def get_weather(self, city: str) -> Dict:
        city = (city or "").strip()
        if not city:
            raise WeatherServiceError("City name cannot be empty")

        params = {
            "q": city,
            "appid": self.api_key,
            "units": Config.UNITS,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                # handle common status codes with user-friendly messages
                if response.status_code == 404:
                    raise WeatherServiceError(f"City '{city}' not found. Check spelling.")
                if response.status_code == 401:
                    raise WeatherServiceError("Invalid API key. Check your .env file.")
                if response.status_code >= 500:
                    raise WeatherServiceError("Weather service unavailable (server error). Try again later.")
                if response.status_code != 200:
                    raise WeatherServiceError(f"Error fetching weather: {response.status_code}")

                return response.json()

        except httpx.TimeoutException:
            raise WeatherServiceError("Request timed out. Check your internet connection.")
        except httpx.NetworkError:
            raise WeatherServiceError("Network error. Check your connection.")
        except Exception as e:
            raise WeatherServiceError(f"Unexpected error: {e}")

    async def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict:
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": Config.UNITS}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                if response.status_code != 200:
                    raise WeatherServiceError(f"Error fetching weather by coordinates: {response.status_code}")
                return response.json()
        except Exception as e:
            raise WeatherServiceError(f"Error fetching weather by coordinates: {e}")
