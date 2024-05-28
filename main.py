import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import os
import schedule
import time
import threading

account_sid = 'ACccb4c5a3ec24961f18993bee99912ebb'
auth_token = 'f5f9dddda69c4eb556f9f31040bffbf7'
client = Client(account_sid, auth_token)

# Function to fetch weather data
def get_weather_data(city):
    query = f"weather in {city}"
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        day = soup.find('div', class_='wob_dts').text
        weather_forecast = soup.find('div', id='wob_dcp').text
        temperature = soup.find('span', class_='wob_t', id='wob_ttm').text

        precipitation = soup.find('span', id='wob_pp').text
        humidity = soup.find('span', id='wob_hm').text
        wind = soup.find('span', id='wob_ws').text

    except AttributeError:
        day = 'Date error'
        weather_forecast = "Unable to retrieve forecast"
        temperature = "Unknown"
        precipitation = "0%"
        humidity = "Unknown"
        wind = "Unknown"

    return day, weather_forecast, temperature, precipitation, humidity, wind

# Function to determine if umbrella is needed
def should_carry_umbrella(precipitation):
    return int(precipitation.strip('%')) > 10

# Function to send WhatsApp message
def send_whatsapp_message(message_body):
    print(f"Sending message: {message_body}")  # Debugging print
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=message_body,
        to='whatsapp:+7984617195'  # Replace with your phone number
    )
    print(f"Message sent: SID={message.sid}")  # Debugging print

# Function to check weather and send message
def check_weather_and_notify():
    print("Checking weather and sending notification...")  # Debugging print
    city = 'mohali'  # Replace with your city
    day, forecast, temperature, precipitation, humidity, wind = get_weather_data(city)
    weather_message = (f"{city}\n{day}\n{forecast}\nTemperature: {temperature}°C\n"
                       f"Precipitation: {precipitation}\nHumidity: {humidity}\nWind: {wind}")
    send_whatsapp_message(weather_message)

    if should_carry_umbrella(precipitation):
        send_whatsapp_message("Remember to carry an umbrella today!")
    else:
        send_whatsapp_message("No need for an umbrella today!")

# Schedule the task for 6 AM every day
schedule.every().day.at("06:00").do(check_weather_and_notify)

# Function to periodically check for changes in precipitation
def monitor_weather_changes():
    city = 'mohali'  # Replace with your city
    _, _, _, precipitation, _, _ = get_weather_data(city)
    initial_precipitation = precipitation
    print("Starting weather change monitoring...")  # Debugging print

    while True:
        time.sleep(3600)  # Check every hour
        print("Checking for weather changes...")  # Debugging print
        _, _, _, new_precipitation, _, _ = get_weather_data(city)
        if new_precipitation != initial_precipitation:
            print(f"Weather changed: {initial_precipitation} -> {new_precipitation}")  # Debugging print
            if should_carry_umbrella(new_precipitation):
                send_whatsapp_message("Weather update: Carry an umbrella!")
            initial_precipitation = new_precipitation

# Start the monitoring process in a separate thread
monitor_thread = threading.Thread(target=monitor_weather_changes)
monitor_thread.daemon = True
monitor_thread.start()

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
