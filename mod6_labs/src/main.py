# main.py
import flet as ft
from weather_service import WeatherService, WeatherServiceError
from config import Config
import asyncio
import json
from pathlib import Path

class HistoryManager:
    def __init__(self, max_items=10):
        self.max_items = max_items
        self.history_file = Path("search_history.json")
        self.history = self._load_history()

    def _load_history(self):
        """Load history from JSON file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('cities', [])[:self.max_items]
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({'cities': self.history}, f, indent=2)
        except IOError as e:
            print(f"Error saving history: {e}")

    def add_city(self, city: str):
        """Add city to history (most recent first)"""
        city = city.strip()
        if not city:
            return
        
        # Remove if already exists (to move to top)
        if city in self.history:
            self.history.remove(city)
        
        # Add to beginning
        self.history.insert(0, city)
        
        # Keep only max_items
        self.history = self.history[:self.max_items]
        
        # Save to file
        self._save_history()

    def get_history(self):
        """Get current history list"""
        return self.history.copy()

    def clear_history(self):
        """Clear all history"""
        self.history = []
        self._save_history()

class PreferencesManager:
    def __init__(self):
        self.prefs_file = Path("user_preferences.json")
        self.preferences = self._load_preferences()

    def _load_preferences(self):
        """Load user preferences from JSON file"""
        if self.prefs_file.exists():
            try:
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"temp_unit": "celsius"}
        return {"temp_unit": "celsius"}

    def _save_preferences(self):
        """Save preferences to JSON file"""
        try:
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2)
        except IOError as e:
            print(f"Error saving preferences: {e}")

    def get_temp_unit(self):
        """Get temperature unit preference"""
        return self.preferences.get("temp_unit", "celsius")

    def set_temp_unit(self, unit: str):
        """Set temperature unit preference"""
        self.preferences["temp_unit"] = unit
        self._save_preferences()

class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history_manager = HistoryManager(max_items=10)
        self.prefs_manager = PreferencesManager()
        self.current_weather_data = None  # Store current weather data
        self.temp_unit = self.prefs_manager.get_temp_unit()  # Load saved preference
        self.setup_page()
        self.build_ui()
        self.load_history_to_ui()

    def setup_page(self):
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
        self.page.padding = 20
        self.page.bgcolor = ft.Colors.WHITE
        self.page.scroll = "auto"
        try:
            self.page.window.resizable = False
            self.page.window.center()
        except Exception:
            pass

    def get_weather_color_scheme(self, weather_main: str, icon_code: str):
        """Get color scheme based on weather condition"""
        weather_main = weather_main.lower()
        
        # Check if it's night time (icon ends with 'n')
        is_night = icon_code.endswith('n')
        
        if is_night:
            return {
                'bg': ft.Colors.INDIGO_900,
                'container': ft.Colors.INDIGO_800,
                'emoji': '🌙',
                'text_color': ft.Colors.WHITE
            }
        elif weather_main == 'clear':
            return {
                'bg': ft.Colors.AMBER_100,
                'container': ft.Colors.AMBER_200,
                'emoji': '☀️',
                'text_color': ft.Colors.ORANGE_900
            }
        elif weather_main == 'clouds':
            return {
                'bg': ft.Colors.BLUE_GREY_100,
                'container': ft.Colors.BLUE_GREY_200,
                'emoji': '☁️',
                'text_color': ft.Colors.BLUE_GREY_900
            }
        elif weather_main == 'rain' or weather_main == 'drizzle':
            return {
                'bg': ft.Colors.LIGHT_BLUE_100,
                'container': ft.Colors.LIGHT_BLUE_200,
                'emoji': '🌧️',
                'text_color': ft.Colors.BLUE_900
            }
        elif weather_main == 'thunderstorm':
            return {
                'bg': ft.Colors.DEEP_PURPLE_100,
                'container': ft.Colors.DEEP_PURPLE_200,
                'emoji': '⛈️',
                'text_color': ft.Colors.DEEP_PURPLE_900
            }
        elif weather_main == 'snow':
            return {
                'bg': ft.Colors.CYAN_50,
                'container': ft.Colors.CYAN_100,
                'emoji': '❄️',
                'text_color': ft.Colors.CYAN_900
            }
        elif weather_main == 'mist' or weather_main == 'fog' or weather_main == 'haze':
            return {
                'bg': ft.Colors.GREY_200,
                'container': ft.Colors.GREY_300,
                'emoji': '🌫️',
                'text_color': ft.Colors.GREY_900
            }
        else:
            return {
                'bg': ft.Colors.LIGHT_BLUE_100,
                'container': ft.Colors.LIGHT_BLUE_200,
                'emoji': '🌤️',
                'text_color': ft.Colors.BLUE_900
            }

    def build_ui(self):
        # Title + theme toggle + unit toggle
        self.title = ft.Text("Weather App", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        
        # Temperature unit toggle button
        self.unit_button = ft.ElevatedButton(
            text="°C" if self.temp_unit == "celsius" else "°F",
            tooltip="Toggle temperature unit",
            on_click=self.toggle_temp_unit,
            bgcolor=ft.Colors.ORANGE_400,
            color=ft.Colors.WHITE,
            width=60,
            height=40
        )
        
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE, 
            tooltip="Toggle theme", 
            on_click=self.toggle_theme,
            icon_color=ft.Colors.BLUE_700
        )

        title_row = ft.Row(
            [
                self.title, 
                ft.Row([self.unit_button, self.theme_button], spacing=5)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Input with search button
        self.city_input = ft.TextField(
            label="Enter city name", 
            hint_text="e.g., London", 
            prefix_icon=ft.Icons.LOCATION_CITY,
            on_submit=self.on_search,
            expand=True,
            bgcolor=ft.Colors.WHITE
        )
        self.search_button = ft.ElevatedButton(
            "Search", 
            icon=ft.Icons.SEARCH, 
            on_click=self.on_search,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE
        )

        search_row = ft.Row(
            [self.city_input, self.search_button],
            spacing=10
        )

        # Recent searches dropdown with clear button
        self.history_dropdown = ft.Dropdown(
            label="Recent searches", 
            options=[], 
            on_change=self.on_history_select,
            bgcolor=ft.Colors.WHITE,
            width=350
        )
        
        self.clear_history_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            tooltip="Clear history",
            on_click=self.on_clear_history,
            icon_color=ft.Colors.RED_400,
            visible=False
        )

        history_row = ft.Row(
            [self.history_dropdown, self.clear_history_button],
            spacing=5
        )

        # Loading and error UI
        self.loading = ft.ProgressRing(visible=False)
        self.error_message = ft.Text("", color=ft.Colors.RED_700, visible=False, size=16)

        # Weather container with animation
        self.weather_container = ft.Container(
            visible=False, 
            padding=30,
            border_radius=12,
            bgcolor=ft.Colors.LIGHT_BLUE_100,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_300,
                offset=ft.Offset(0, 4),
            ),
            animate=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
        )

        # Layout
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    search_row,
                    history_row,
                    ft.Row([self.loading], alignment=ft.MainAxisAlignment.CENTER),
                    self.error_message,
                    self.weather_container,
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        )

    def load_history_to_ui(self):
        """Load saved history into dropdown on app start"""
        history = self.history_manager.get_history()
        if history:
            self.history_dropdown.options = [ft.dropdown.Option(c) for c in history]
            self.clear_history_button.visible = True
        self.page.update()

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
            self.page.bgcolor = ft.Colors.BLUE_GREY_900
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
            self.page.bgcolor = ft.Colors.WHITE
        self.page.update()

    def toggle_temp_unit(self, e):
        """Toggle between Celsius and Fahrenheit"""
        if self.temp_unit == "celsius":
            self.temp_unit = "fahrenheit"
            self.unit_button.text = "°F"
        else:
            self.temp_unit = "celsius"
            self.unit_button.text = "°C"
        
        # Save preference
        self.prefs_manager.set_temp_unit(self.temp_unit)
        
        # Redisplay current weather if available
        if self.current_weather_data:
            self.page.run_task(self.display_weather, self.current_weather_data)
        
        self.page.update()

    def celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convert Celsius to Fahrenheit"""
        return (celsius * 9/5) + 32

    def get_temp_display(self, temp_celsius: float) -> str:
        """Get temperature display based on current unit preference"""
        if self.temp_unit == "fahrenheit":
            temp_f = self.celsius_to_fahrenheit(temp_celsius)
            return f"{temp_f:.1f}°F"
        else:
            return f"{temp_celsius:.1f}°C"

    def on_history_select(self, e):
        value = e.control.value
        if value:
            self.city_input.value = value
            self.page.update()
            self.page.run_task(self.get_weather)

    def on_search(self, e):
        self.page.run_task(self.get_weather)

    def on_clear_history(self, e):
        """Clear search history and reset dropdown completely"""
        self.history_manager.clear_history()
        self.history_dropdown.options = []
        self.history_dropdown.value = None
        self.history_dropdown.error_text = None
        self.clear_history_button.visible = False
        self.page.update()

    async def get_weather(self):
        city = (self.city_input.value or "").strip()
        if not city:
            self.show_error("Please enter a city name")
            return

        # Reset dropdown selection when manually searching
        self.history_dropdown.value = None
        
        # UI state: show loading
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()

        try:
            data = await self.weather_service.get_weather(city)
            self.current_weather_data = data  # Store current weather data
            self.add_to_history(city)
            await self.display_weather(data)
        except WeatherServiceError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error("An unexpected error occurred.")
            print("DEBUG:", e)
        finally:
            self.loading.visible = False
            self.page.update()

    def add_to_history(self, city: str):
        """Add city to persistent history"""
        city = city.strip()
        if city:
            self.history_manager.add_city(city)
            history = self.history_manager.get_history()
            self.history_dropdown.options = [ft.dropdown.Option(c) for c in history]
            self.clear_history_button.visible = len(history) > 0
            self.page.update()

    async def display_weather(self, data: dict):
        # Extract data (always in Celsius from API)
        name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0.0)
        feels_like = data.get("main", {}).get("feels_like", 0.0)
        temp_min = data.get("main", {}).get("temp_min", 0.0)
        temp_max = data.get("main", {}).get("temp_max", 0.0)
        humidity = data.get("main", {}).get("humidity", 0)
        pressure = data.get("main", {}).get("pressure", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        weather_main = data.get("weather", [{}])[0].get("main", "Clear")
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        cloudiness = data.get("clouds", {}).get("all", 0)

        # Get color scheme based on weather
        color_scheme = self.get_weather_color_scheme(weather_main, icon_code)
        
        # Update page background with smooth transition
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.bgcolor = color_scheme['bg']
        
        # Build content with temperature conversion
        content = ft.Column(
            [
                # Weather emoji badge
                ft.Container(
                    content=ft.Text(color_scheme['emoji'], size=60),
                    alignment=ft.alignment.center,
                ),
                
                # Location with pin icon
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED, size=24),
                        ft.Text(f"{name}, {country}", size=24, weight=ft.FontWeight.BOLD, color=color_scheme['text_color'])
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                
                # Weather icon from API
                ft.Row(
                    [ft.Image(src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png", width=120, height=120)],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                
                # Description
                ft.Text(description, size=18, italic=True, color=color_scheme['text_color'], text_align=ft.TextAlign.CENTER),
                
                # Main temperature (converted)
                ft.Text(self.get_temp_display(temp), size=48, weight=ft.FontWeight.BOLD, color=color_scheme['text_color']),
                
                # Feels like (converted)
                ft.Text(f"Feels like {self.get_temp_display(feels_like)}", size=14, color=color_scheme['text_color']),
                
                # Temperature range (converted)
                ft.Row(
                    [
                        ft.Text(f"↑ {self.get_temp_display(temp_max)}", size=14, color=ft.Colors.RED_700),
                        ft.Text(f"↓ {self.get_temp_display(temp_min)}", size=14, color=ft.Colors.BLUE_700),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                
                ft.Divider(height=20, color=color_scheme['text_color'], opacity=0.3),
                
                # Info cards in 2x2 grid
                ft.Row(
                    [
                        self.create_info_card(ft.Icons.WATER_DROP, "Humidity", f"{humidity}%", ft.Colors.BLUE_400),
                        self.create_info_card(ft.Icons.AIR, "Wind Speed", f"{wind_speed} m/s", ft.Colors.CYAN_400),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                    wrap=True
                ),
                ft.Row(
                    [
                        self.create_info_card(ft.Icons.COMPRESS, "Pressure", f"{pressure} hPa", ft.Colors.PURPLE_400),
                        self.create_info_card(ft.Icons.CLOUD, "Cloudiness", f"{cloudiness}%", ft.Colors.GREY_600),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                    wrap=True
                ),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Update container with new color scheme
        self.weather_container.content = content
        self.weather_container.bgcolor = color_scheme['container']
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.weather_container.animate_opacity = 300
        self.page.update()

        await asyncio.sleep(0.05)
        self.weather_container.opacity = 1
        self.page.update()

    def create_info_card(self, icon, label, value, icon_color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=32, color=icon_color),
                    ft.Text(label, size=13, color=ft.Colors.BLUE_800),
                    ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            border_radius=10,
            width=180,
            height=120,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.BLUE_GREY_200,
                offset=ft.Offset(0, 2),
            )
        )

    def show_error(self, message: str):
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        # Reset background to default on error
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.bgcolor = ft.Colors.WHITE
        self.page.update()

def main(page: ft.Page):
    WeatherApp(page)

if __name__ == "__main__":
    ft.app(target=main)