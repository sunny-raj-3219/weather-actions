import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import os
from datetime import datetime

# Twilio client setup
account_sid = 'ACccb4c5a3ec24961f18993bee99912ebb'
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

my_phone_no = os.environ.get('MY_PHONE_NO')


def get_weather_data(city):
    query = f"weather in {city}"
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
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


def should_carry_umbrella(precipitation):
    return int(precipitation.strip('%')) > 10


def send_whatsapp_message(message_body):
    my_phone_no = os.environ.get('MY_PHONE_NO')
    message = client.messages.create(from_='whatsapp:+14155238886',
                                     body=message_body,
                                     to=f'whatsapp:{my_phone_no}')

                                    


def send_daily_weather_update():
    city = 'gharuan'
    day, forecast, temperature, precipitation, humidity, wind = get_weather_data(
        city)
    weather_message = f"{city}\n{day}\n{forecast}\nTemperature: {temperature}°C\nPrecipitation: {precipitation}\nHumidity: {humidity}\nWind: {wind}"
    send_whatsapp_message(weather_message)
    if should_carry_umbrella(precipitation):
        send_whatsapp_message("Remember to carry an umbrella today!")
    else:
        send_whatsapp_message("No need for an umbrella today!")
    print(f"Daily weather message sent: \n{weather_message}")


def send_precipitation_alert():
    city = 'gharuan'
    _, _, _, precipitation, _, _ = get_weather_data(city)
    if should_carry_umbrella(precipitation):
        alert_message = "Chances of precipitation > 10%. Remember to carry an umbrella!"
        send_whatsapp_message(alert_message)
        print(f"Precipitation alert message sent: \n{alert_message}")


def check_precipitation_change():
    city = 'gharuan'
    _, _, _, precipitation, _, _ = get_weather_data(city)

    # Read previous precipitation value from file
    try:
        with open('last_precipitation.txt', 'r') as file:
            last_precipitation = file.read().strip()
    except FileNotFoundError:
        last_precipitation = "0%"

    # Update file with current precipitation
    with open('last_precipitation.txt', 'w') as file:
        file.write(precipitation)

    if last_precipitation != precipitation and should_carry_umbrella(
            precipitation):
        send_precipitation_alert()


# Determine which function to run based on the current time
current_hour = datetime.now().hour

if current_hour == 6:
    send_daily_weather_update()
else:
    check_precipitation_change()
print('running...')
