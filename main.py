import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import os
import schedule
import time

account_sid = 'ACccb4c5a3ec24961f18993bee99912ebb'
auth_token = os.environ.get('A')
client = Client(account_sid, auth_token)


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


def should_carry_umbrella(forecast, precipitation):
    if int(precipitation.strip('%')) > 10:

        return True
    return False


def send_whatsapp_message(message_body):
    message = client.messages.create(from_='whatsapp:+14155238886',
                                     body=message_body,
                                     to='whatsapp:+917984617195')


city = 'gharuan'
day, forecast, temperature, precipitation, humidity, wind = get_weather_data(
    city)

weather_message = f"{city}\n{day}\n{forecast}\nTemperature: {temperature}°C\nPrecipitation: {precipitation}\nHumidity: {humidity}\nWind: {wind}"

send_whatsapp_message(weather_message)

if should_carry_umbrella(forecast, precipitation):
    send_whatsapp_message("Remember to carry an umbrella today!")
else:
    send_whatsapp_message("No need for an umbrella today!")

print(f"Weather message sent: \n{weather_message}")
