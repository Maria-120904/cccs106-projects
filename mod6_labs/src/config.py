# config.py
"""Configuration management for the Weather App."""

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env from project root

class Config:
    # API
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
    BASE_URL = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5/weather").strip()

    # App UI
    APP_TITLE = os.getenv("APP_TITLE", "Weather App")
    APP_WIDTH = int(os.getenv("APP_WIDTH", 400))
    APP_HEIGHT = int(os.getenv("APP_HEIGHT", 600))

    # API behavior
    UNITS = os.getenv("UNITS", "metric")  # metric, imperial, standard
    TIMEOUT = float(os.getenv("TIMEOUT", 10.0))

    @classmethod
    def validate(cls):
        if not cls.API_KEY:
            raise ValueError("OPENWEATHER_API_KEY missing. Copy .env.example to .env and set your API key.")
        # small validation for units
        if cls.UNITS not in ("metric", "imperial", "standard"):
            cls.UNITS = "metric"
        return True

# Validate when importing
Config.validate()
