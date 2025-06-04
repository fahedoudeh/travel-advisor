import requests
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich import box

# Initialize Rich console
console = Console()

# API URLs
RESTCOUNTRIES_URL = "https://restcountries.com/v3.1"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
TRAVEL_ADVISORY_URL = "https://www.travel-advisory.info/api"
NAGER_DATE_URL = "https://date.nager.at/api/v3"

# Function to get country information by name
def get_country_info(country_name):
    try:
        response = requests.get(f"{RESTCOUNTRIES_URL}/name/{country_name}")
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[bold red]Error:[/bold red] Could not find country '{country_name}'")
            return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return None

# Function to get country information by capital city
def get_country_by_capital(capital_name):
    try:
        response = requests.get(f"{RESTCOUNTRIES_URL}/capital/{capital_name}")
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[bold red]Error:[/bold red] Could not find country with capital '{capital_name}'")
            return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
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
            console.print(f"[bold red]Error:[/bold red] Could not get weather data for coordinates {latitude}, {longitude}")
            return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return None

# Function to get travel advisory information
def get_travel_advisory(country_code):
    try:
        # Added verify=False to fix SSL certificate issue
        response = requests.get(f"{TRAVEL_ADVISORY_URL}?countrycode={country_code}", verify=False)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "ok" and country_code in data["data"]:
                return data["data"][country_code]
            else:
                console.print(f"[bold yellow]Warning:[/bold yellow] No travel advisory data available for {country_code}")
                return None
        else:
            console.print(f"[bold red]Error:[/bold red] Could not get travel advisory data")
            return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold yellow]Warning:[/bold yellow] Travel advisory service unavailable: {e}")
        return None

# Function to get public holidays for a country
def get_holidays(country_code, year=2025):
    try:
        response = requests.get(f"{NAGER_DATE_URL}/PublicHolidays/{year}/{country_code}")
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[bold yellow]Warning:[/bold yellow] No holiday data available for {country_code}")
            return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold yellow]Warning:[/bold yellow] Holiday service unavailable: {e}")
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
    
    # Create country info table
    country_table = Table(title=f"Country Information: {country.get('name', {}).get('common', 'N/A')}", 
                         box=box.ROUNDED, 
                         show_header=False,
                         title_style="bold cyan")
    
    country_table.add_column("Property", style="bold green")
    country_table.add_column("Value", style="yellow")
    
    country_table.add_row("Capital", ", ".join(country.get('capital', ['N/A'])))
    country_table.add_row("Region", country.get('region', 'N/A'))
    country_table.add_row("Population", f"{country.get('population', 'N/A'):,}")
    
    # Languages
    if 'languages' in country:
        languages = ", ".join(country['languages'].values())
        country_table.add_row("Languages", languages)
    
    # Currency
    if 'currencies' in country:
        currencies = []
        for currency_code, currency_info in country['currencies'].items():
            currencies.append(f"{currency_info.get('name', 'Unknown')} ({currency_code})")
        country_table.add_row("Currencies", ", ".join(currencies))
    
    console.print(country_table)
    
    # Create weather table
    weather_table = Table(title="Current Weather", box=box.ROUNDED, show_header=False, title_style="bold cyan")
    weather_table.add_column("Property", style="bold green")
    weather_table.add_column("Value", style="yellow")
    
    current = weather_data.get("current_weather", {})
    weather_table.add_row("Temperature", f"{current.get('temperature', 'N/A')}°C")
    weather_table.add_row("Wind Speed", f"{current.get('windspeed', 'N/A')} km/h")
    
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
    
    weather_table.add_row("Weather Condition", weather_description)
    
    console.print(weather_table)
    
    # Display travel advice
    advice = get_weather_advice(weather_data)
    console.print(Panel(advice, title="Travel Advice", border_style="green"))
    
    # Get and display travel advisory if available
    if 'cca2' in country:
        country_code = country['cca2']
        advisory_data = get_travel_advisory(country_code)
        
        if advisory_data:
            advisory_score = advisory_data.get('advisory', {}).get('score', 'N/A')
            advisory_message = advisory_data.get('advisory', {}).get('message', 'No specific advisory message')
            
            # Create color based on advisory score
            color = "green"
            if advisory_score != 'N/A':
                if advisory_score > 4:
                    color = "red"
                elif advisory_score > 2.5:
                    color = "yellow"
            
            console.print(Panel(
                f"Advisory Score: [bold {color}]{advisory_score}[/bold {color}] (lower is better)\n{advisory_message}",
                title="Travel Advisory Information",
                border_style=color
            ))
    
    # Get and display holidays if available
    if 'cca2' in country:
        country_code = country['cca2']
        holidays = get_holidays(country_code)
        
        if holidays and len(holidays) > 0:
            holiday_table = Table(title="Upcoming Public Holidays", box=box.ROUNDED, title_style="bold cyan")
            holiday_table.add_column("Date", style="cyan")
            holiday_table.add_column("Holiday", style="yellow")
            holiday_table.add_column("Type", style="green")
            
            # Display up to 5 upcoming holidays
            for holiday in holidays[:5]:
                holiday_table.add_row(
                    holiday.get('date', 'N/A'),
                    holiday.get('name', 'N/A'),
                    holiday.get('types', ['N/A'])[0] if holiday.get('types') else 'N/A'
                )
            
            console.print(holiday_table)

# Function to compare weather between two locations
def compare_weather(location1_data, weather1_data, location2_data, weather2_data):
    if not location1_data or not weather1_data or not location2_data or not weather2_data:
        return
    
    location1 = location1_data[0]["name"]["common"]
    location2 = location2_data[0]["name"]["common"]
    
    console.print(f"\n[bold cyan]===== WEATHER COMPARISON: {location1} vs {location2} =====[/bold cyan]")
    
    # Create comparison table
    comparison_table = Table(title=f"Weather Comparison", box=box.ROUNDED, title_style="bold cyan")
    comparison_table.add_column("Metric", style="bold green")
    comparison_table.add_column(location1, style="yellow")
    comparison_table.add_column(location2, style="cyan")
    comparison_table.add_column("Difference/Notes", style="magenta")
    
    # Temperature comparison
    temp1 = weather1_data["current_weather"]["temperature"]
    temp2 = weather2_data["current_weather"]["temperature"]
    temp_diff = abs(temp1 - temp2)
    
    temp_note = ""
    if temp1 > temp2:
        temp_note = f"{location1} is warmer by {temp_diff:.1f}°C"
    elif temp2 > temp1:
        temp_note = f"{location2} is warmer by {temp_diff:.1f}°C"
    else:
        temp_note = "Same temperature"
    
    comparison_table.add_row("Temperature", f"{temp1}°C", f"{temp2}°C", temp_note)
    
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
    
    weather_note = ""
    if weathercode1 < weathercode2:  # Lower codes generally mean better weather
        weather_note = f"{location1} has better conditions"
    elif weathercode2 < weathercode1:
        weather_note = f"{location2} has better conditions"
    else:
        weather_note = "Similar conditions"
    
    comparison_table.add_row("Weather", weather_desc1, weather_desc2, weather_note)
    
    # Wind comparison
    wind1 = weather1_data["current_weather"]["windspeed"]
    wind2 = weather2_data["current_weather"]["windspeed"]
    wind_diff = abs(wind1 - wind2)
    
    wind_note = ""
    if wind1 > wind2:
        wind_note = f"{location1} is windier by {wind_diff:.1f} km/h"
    elif wind2 > wind1:
        wind_note = f"{location2} is windier by {wind_diff:.1f} km/h"
    else:
        wind_note = "Same wind speed"
    
    comparison_table.add_row("Wind Speed", f"{wind1} km/h", f"{wind2} km/h", wind_note)
    
    console.print(comparison_table)
    
    # Travel recommendation
    if weathercode1 < weathercode2 and temp1 > 15 and temp1 < 30:
        recommendation = f"[bold green]{location1}[/bold green] currently has better weather conditions for traveling."
    elif weathercode2 < weathercode1 and temp2 > 15 and temp2 < 30:
        recommendation = f"[bold green]{location2}[/bold green] currently has better weather conditions for traveling."
    else:
        if temp1 > 15 and temp1 < 30 and not (temp2 > 15 and temp2 < 30):
            recommendation = f"[bold green]{location1}[/bold green] has more comfortable temperatures for traveling."
        elif temp2 > 15 and temp2 < 30 and not (temp1 > 15 and temp1 < 30):
            recommendation = f"[bold green]{location2}[/bold green] has more comfortable temperatures for traveling."
        else:
            recommendation = "Both locations have [bold yellow]similar[/bold yellow] weather conditions for traveling."
    
    console.print(Panel(recommendation, title="Travel Recommendation", border_style="green"))
    
    # Add specific advice for each location
    console.print(Panel(
        f"[bold yellow]{location1}:[/bold yellow] {get_weather_advice(weather1_data)}\n\n"
        f"[bold cyan]{location2}:[/bold cyan] {get_weather_advice(weather2_data)}",
        title="Detailed Travel Advice",
        border_style="blue"
    ))
    
    # Compare languages if available
    if 'languages' in location1_data[0] and 'languages' in location2_data[0]:
        languages1 = ", ".join(location1_data[0]['languages'].values())
        languages2 = ", ".join(location2_data[0]['languages'].values())
        
        language_table = Table(title="Language Comparison", box=box.ROUNDED, title_style="bold cyan")
        language_table.add_column(location1, style="yellow")
        language_table.add_column(location2, style="cyan")
        
        language_table.add_row(languages1, languages2)
        console.print(language_table)

# Main menu function
def main_menu():
    while True:
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]TRAVEL & WEATHER ADVISOR[/bold cyan]\n\n"
            "Your comprehensive travel companion for weather and country information",
            border_style="cyan",
            padding=(1, 10)
        ))
        
        console.print("[bold green]1.[/bold green] Get Country/City Information and Weather")
        console.print("[bold green]2.[/bold green] Compare Weather Between Two Locations")
        console.print("[bold green]3.[/bold green] Exit")
        
        choice = Prompt.ask("\nEnter your choice", choices=["1", "2", "3"], default="1")
        
        if choice == "1":
            console.clear()
            console.print(Panel("Country/City Information and Weather", border_style="cyan"))
            
            location_type = Prompt.ask("Search by country name or capital city?", choices=["country", "capital"], default="country")
            location_name = Prompt.ask("Enter the name")
            
            with console.status(f"[bold green]Searching for {location_name}...[/bold green]"):
                country_data = None
                if location_type == "country":
                    country_data = get_country_info(location_name)
                elif location_type == "capital":
                    country_data = get_country_by_capital(location_name)
                
                if country_data:
                    # Get coordinates for weather data
                    lat = country_data[0]["latlng"][0]
                    lon = country_data[0]["latlng"][1]
                    
                    # Get weather data
                    weather_data = get_weather(lat, lon)
                    
                    # Display information
                    console.clear()
                    display_country_weather_info(country_data, weather_data)
            
        elif choice == "2":
            console.clear()
            console.print(Panel("Compare Weather Between Two Locations", border_style="cyan"))
            
            console.print("[bold yellow]First location:[/bold yellow]")
            location1_type = Prompt.ask("Search by country name or capital city?", choices=["country", "capital"], default="country")
            location1_name = Prompt.ask("Enter the name")
            
            with console.status(f"[bold green]Searching for {location1_name}...[/bold green]"):
                location1_data = None
                if location1_type == "country":
                    location1_data = get_country_info(location1_name)
                elif location1_type == "capital":
                    location1_data = get_country_by_capital(location1_name)
                
                if not location1_data:
                    console.print("[bold red]Could not find the first location. Please try again.[/bold red]")
                    continue
            
            console.print("\n[bold cyan]Second location:[/bold cyan]")
            location2_type = Prompt.ask("Search by country name or capital city?", choices=["country", "capital"], default="country")
            location2_name = Prompt.ask("Enter the name")
            
            with console.status(f"[bold green]Searching for {location2_name}...[/bold green]"):
                location2_data = None
                if location2_type == "country":
                    location2_data = get_country_info(location2_name)
                elif location2_type == "capital":
                    location2_data = get_country_by_capital(location2_name)
                
                if not location2_data:
                    console.print("[bold red]Could not find the second location. Please try again.[/bold red]")
                    continue
            
            with console.status("[bold green]Getting weather data and comparing...[/bold green]"):
                # Get coordinates for weather data
                lat1 = location1_data[0]["latlng"][0]
                lon1 = location1_data[0]["latlng"][1]
                lat2 = location2_data[0]["latlng"][0]
                lon2 = location2_data[0]["latlng"][1]
                
                # Get weather data
                weather1_data = get_weather(lat1, lon1)
                weather2_data = get_weather(lat2, lon2)
                
                # Compare weather
                console.clear()
                compare_weather(location1_data, weather1_data, location2_data, weather2_data)
            
        elif choice == "3":
            console.print(Panel("Thank you for using the Travel & Weather Advisor. Goodbye!", 
                               border_style="green"))
            sys.exit(0)
        
        console.print("\nPress Enter to continue...", style="bold")
        input()

# Run the application
if __name__ == "__main__":
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]Welcome to the Travel & Weather Advisor![/bold cyan]\n\n"
        "This application helps you get information about countries, their weather conditions, "
        "travel advisories, languages, and upcoming holidays.",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    # Disable SSL warnings that might appear due to verify=False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    console.print("\nPress Enter to start...", style="bold")
    input()
    main_menu()