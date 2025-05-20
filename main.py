import requests
import json
import sys

# API URLs
RESTCOUNTRIES_URL = "https://restcountries.com/v3.1"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Function to get country information by name
def get_country_info(country_name):
    try:
        response = requests.get(f"{RESTCOUNTRIES_URL}/name/{country_name}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Could not find country '{country_name}'")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Function to get country information by capital city
def get_country_by_capital(capital_name):
    try:
        response = requests.get(f"{RESTCOUNTRIES_URL}/capital/{capital_name}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Could not find country with capital '{capital_name}'")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Function to get weather information by coordinates
def get_weather(latitude, longitude):
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
            "hourly": "temperature_2m,precipitation_probability,weathercode"
        }
        response = requests.get(OPEN_METEO_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Could not get weather data for coordinates {latitude}, {longitude}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Function to get weather advice based on weather data
def get_weather_advice(weather_data):
    if not weather_data or "current_weather" not in weather_data:
        return "No weather data available to provide advice."
    
    temperature = weather_data["current_weather"]["temperature"]
    weathercode = weather_data["current_weather"]["weathercode"]
    
    # Weather codes reference: https://open-meteo.com/en/docs
    # 0: Clear sky, 1-3: Mainly clear/partly cloudy, 45-48: Fog, 51-67: Rain, 71-77: Snow, 80-99: Rain showers
    
    advice = ""
    
    # Temperature-based advice
    if temperature > 30:
        advice += "It's very hot! Stay hydrated and seek shade. "
    elif temperature > 25:
        advice += "It's quite warm. Sunscreen recommended. "
    elif temperature > 15:
        advice += "The temperature is pleasant. "
    elif temperature > 5:
        advice += "It's a bit cool. Consider bringing a light jacket. "
    elif temperature > 0:
        advice += "It's cold. Warm clothing recommended. "
    else:
        advice += "It's freezing! Bundle up with warm layers. "
    
    # Weather condition-based advice
    if weathercode == 0:
        advice += "Clear skies are perfect for outdoor activities!"
    elif weathercode in [1, 2, 3]:
        advice += "Partly cloudy conditions are good for sightseeing."
    elif weathercode in [45, 48]:
        advice += "Be careful when traveling due to fog conditions."
    elif weathercode in range(51, 68):
        advice += "Bring an umbrella as rain is expected."
    elif weathercode in range(71, 78):
        advice += "Snow is expected. Dress warmly and check road conditions."
    elif weathercode in range(80, 100):
        advice += "Rain showers are expected. Plan indoor activities or bring rain gear."
    
    return advice

# Function to display country and weather information
def display_country_weather_info(country_data, weather_data):
    if not country_data or not weather_data:
        return
    
    country = country_data[0]  # Take the first result
    
    print("\n===== COUNTRY INFORMATION =====")
    print(f"Country: {country.get('name', {}).get('common', 'N/A')}")
    print(f"Capital: {', '.join(country.get('capital', ['N/A']))}")
    print(f"Region: {country.get('region', 'N/A')}")
    print(f"Population: {country.get('population', 'N/A'):,}")
    
    print("\n===== CURRENT WEATHER =====")
    current = weather_data.get("current_weather", {})
    print(f"Temperature: {current.get('temperature', 'N/A')}°C")
    print(f"Wind Speed: {current.get('windspeed', 'N/A')} km/h")
    
    # Get weather code description
    weathercode = current.get('weathercode', None)
    weather_description = "Unknown"
    if weathercode == 0:
        weather_description = "Clear sky"
    elif weathercode in [1, 2, 3]:
        weather_description = "Partly cloudy"
    elif weathercode in [45, 48]:
        weather_description = "Fog"
    elif weathercode in range(51, 68):
        weather_description = "Rain"
    elif weathercode in range(71, 78):
        weather_description = "Snow"
    elif weathercode in range(80, 100):
        weather_description = "Rain showers"
    
    print(f"Weather Condition: {weather_description}")
    
    print("\n===== TRAVEL ADVICE =====")
    print(get_weather_advice(weather_data))
    print()

# Function to compare weather between two locations
def compare_weather(location1_data, weather1_data, location2_data, weather2_data):
    if not location1_data or not weather1_data or not location2_data or not weather2_data:
        return
    
    location1 = location1_data[0]["name"]["common"]
    location2 = location2_data[0]["name"]["common"]
    
    print(f"\n===== WEATHER COMPARISON: {location1} vs {location2} =====")
    
    # Temperature comparison
    temp1 = weather1_data["current_weather"]["temperature"]
    temp2 = weather2_data["current_weather"]["temperature"]
    temp_diff = abs(temp1 - temp2)
    
    print(f"Temperature in {location1}: {temp1}°C")
    print(f"Temperature in {location2}: {temp2}°C")
    print(f"Temperature difference: {temp_diff:.1f}°C")
    
    if temp1 > temp2:
        print(f"{location1} is warmer than {location2} by {temp_diff:.1f}°C")
    elif temp2 > temp1:
        print(f"{location2} is warmer than {location1} by {temp_diff:.1f}°C")
    else:
        print(f"Both locations have the same temperature.")
    
    # Weather condition comparison
    weathercode1 = weather1_data["current_weather"]["weathercode"]
    weathercode2 = weather2_data["current_weather"]["weathercode"]
    
    # Get weather descriptions
    weather_descriptions = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers"
    }
    
    weather_desc1 = weather_descriptions.get(weathercode1, "Unknown")
    weather_desc2 = weather_descriptions.get(weathercode2, "Unknown")
    
    print(f"Weather in {location1}: {weather_desc1}")
    print(f"Weather in {location2}: {weather_desc2}")
    
    # Travel recommendation
    print("\n===== TRAVEL RECOMMENDATION =====")
    if weathercode1 < weathercode2:  # Lower codes generally mean better weather
        print(f"{location1} currently has better weather conditions for traveling.")
    elif weathercode2 < weathercode1:
        print(f"{location2} currently has better weather conditions for traveling.")
    else:
        print("Both locations have similar weather conditions.")
    
    # Add specific advice for each location
    print(f"\nAdvice for {location1}: {get_weather_advice(weather1_data)}")
    print(f"Advice for {location2}: {get_weather_advice(weather2_data)}")
    print()

# Main menu function
def main_menu():
    while True:
        print("\n===== TRAVEL & WEATHER ADVISOR =====")
        print("1. Get Country/City Information and Weather")
        print("2. Compare Weather Between Two Locations")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            location_type = input("\nSearch by country name or capital city? (country/capital): ").lower()
            location_name = input("Enter the name: ")
            
            country_data = None
            if location_type == "country":
                country_data = get_country_info(location_name)
            elif location_type == "capital":
                country_data = get_country_by_capital(location_name)
            else:
                print("Invalid option. Please enter 'country' or 'capital'.")
                continue
            
            if country_data:
                # Get coordinates for weather data
                lat = country_data[0]["latlng"][0]
                lon = country_data[0]["latlng"][1]
                
                # Get weather data
                weather_data = get_weather(lat, lon)
                
                # Display information
                display_country_weather_info(country_data, weather_data)
            
        elif choice == "2":
            print("\nFirst location:")
            location1_type = input("Search by country name or capital city? (country/capital): ").lower()
            location1_name = input("Enter the name: ")
            
            location1_data = None
            if location1_type == "country":
                location1_data = get_country_info(location1_name)
            elif location1_type == "capital":
                location1_data = get_country_by_capital(location1_name)
            else:
                print("Invalid option. Please enter 'country' or 'capital'.")
                continue
            
            print("\nSecond location:")
            location2_type = input("Search by country name or capital city? (country/capital): ").lower()
            location2_name = input("Enter the name: ")
            
            location2_data = None
            if location2_type == "country":
                location2_data = get_country_info(location2_name)
            elif location2_type == "capital":
                location2_data = get_country_by_capital(location2_name)
            else:
                print("Invalid option. Please enter 'country' or 'capital'.")
                continue
            
            if location1_data and location2_data:
                # Get coordinates for weather data
                lat1 = location1_data[0]["latlng"][0]
                lon1 = location1_data[0]["latlng"][1]
                lat2 = location2_data[0]["latlng"][0]
                lon2 = location2_data[0]["latlng"][1]
                
                # Get weather data
                weather1_data = get_weather(lat1, lon1)
                weather2_data = get_weather(lat2, lon2)
                
                # Compare weather
                compare_weather(location1_data, weather1_data, location2_data, weather2_data)
            
        elif choice == "3":
            print("Thank you for using the Travel & Weather Advisor. Goodbye!")
            sys.exit(0)
        
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")
        
        input("\nPress Enter to continue...")

# Run the application
if __name__ == "__main__":
    print("Welcome to the Travel & Weather Advisor!")
    print("This application helps you get information about countries and their weather conditions.")
    main_menu()
