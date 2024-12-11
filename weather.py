import requests
from datetime import datetime, timedelta
import re

def get_coordinates(location):
    """Fetch the coordinates (latitude, longitude) for a given location using OpenCage API."""
    api_key = "4d0cd98023ab414a9ed6be1325cda9bd"  # Replace with your OpenCage API key
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": location, "key": api_key}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['results']:
            coords = data['results'][0]['geometry']
            print(f"Coordinates fetched: {coords['lat']}, {coords['lng']}")
            return coords['lat'], coords['lng']
        else:
            print("No results found for the location.")
            return None, None
    else:
        print("Error fetching coordinates:", response.status_code, response.text)
        return None, None

def get_weather_data(lat, lon, api_key):
    """Fetch the weather forecast using OpenWeatherMap API."""
    base_url = "https://api.openweathermap.org/data/2.5/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "minutely,hourly",
        "units": "metric",
        "appid": api_key
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching weather data:", response.status_code, response.text)
        return None

def filter_forecast(forecast_data, start_date, end_date):
    """Filter the forecast data for the given date range."""
    daily_forecasts = forecast_data.get('daily', [])
    filtered_forecast = []

    for day in daily_forecasts:
        period_date = datetime.utcfromtimestamp(day['dt']).date()
        if start_date <= period_date <= end_date:
            filtered_forecast.append(day)

    return filtered_forecast

def main():
    api_key = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with your OpenWeatherMap API key

    location_input = input("Enter a location (city, zip code) [Ex: Tokyo, 100-0001]: ")

    # Validate the input format using regex
    if not re.match(r"^[\w\s]+,\s*\d{3}-\d{4}$", location_input):
        print("Invalid location format. Please use the format 'City, ZIP Code' (e.g., Tokyo, 100-0001).")
        return

    # Split into city and zip code
    city, zip_code = map(str.strip, location_input.split(","))
    location = f"{city}, {zip_code}"  # Recombine for query

    # Get start and end dates
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

    # Validate and convert dates
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        if (end_date - start_date).days > 7:
            print("Date range cannot exceed 7 days.")
            return
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # Get coordinates
    lat, lon = get_coordinates(location)
    if lat is None or lon is None:
        return

    # Get weather data
    weather_data = get_weather_data(lat, lon, api_key)
    if weather_data is None:
        return

    # Filter and display the forecast
    forecast = filter_forecast(weather_data, start_date, end_date)
    if not forecast:
        print("No weather data available for the given date range.")
        return

    for day in forecast:
        date = datetime.utcfromtimestamp(day['dt']).strftime("%Y-%m-%d")
        temp_day = day['temp']['day']
        temp_night = day['temp']['night']
        weather_desc = day['weather'][0]['description']
        print(f"Date: {date}")
        print(f"Day Temperature: {temp_day} °C")
        print(f"Night Temperature: {temp_night} °C")
        print(f"Weather: {weather_desc.capitalize()}\n")

if __name__ == "__main__":
    main()
