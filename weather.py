import requests
from datetime import datetime, timedelta
import re

def get_coordinates(location):
    """Fetch the coordinates (latitude, longitude) for a given location."""
    base_url = "https://geocode.xyz"
    params = {"locate": location, "json": 1}
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        try:
            return float(data['latt']), float(data['longt'])
        except KeyError:
            print("Could not find coordinates for the location.")
            return None, None
    else:
        print("Error fetching coordinates:", response.status_code)
        return None, None

def get_weather_data(lat, lon):
    """Fetch the weather forecast from the National Weather Service API."""
    base_url = f"https://api.weather.gov/points/{lat},{lon}"
    response = requests.get(base_url)
    
    if response.status_code == 200:
        data = response.json()
        forecast_url = data['properties']['forecast']
        forecast_response = requests.get(forecast_url)
        if forecast_response.status_code == 200:
            return forecast_response.json()
        else:
            print("Error fetching forecast:", forecast_response.status_code)
            return None
    else:
        print("Error fetching weather data:", response.status_code)
        return None

def filter_forecast(forecast_data, start_date, end_date):
    """Filter the forecast data for the given date range."""
    forecasts = forecast_data['properties']['periods']
    filtered_forecast = []
    
    for period in forecasts:
        period_date = datetime.strptime(period['startTime'], "%Y-%m-%dT%H:%M:%S%z").date()
        if start_date <= period_date <= end_date:
            filtered_forecast.append(period)
    
    return filtered_forecast

def main():
    location = input("Enter a location (city, state, or zip): ")
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
    
    lat, lon = get_coordinates(location)
    if lat is None or lon is None:
        return
    
    weather_data = get_weather_data(lat, lon)
    if weather_data is None:
        return
    
    forecast = filter_forecast(weather_data, start_date, end_date)
    if not forecast:
        print("No weather data available for the given date range.")
        return
    
    for day in forecast:
        print(f"Date: {day['startTime']}")
        print(f"Temperature: {day['temperature']} {day['temperatureUnit']}")
        print(f"Short Forecast: {day['shortForecast']}")
        print(f"Detailed Forecast: {day['detailedForecast']}\n")

if __name__ == "__main__":
    main()
