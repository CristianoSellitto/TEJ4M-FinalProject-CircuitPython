'''
- By Cristiano
- Created December 2023

This program write the current weather in Mont Tremblant to a Adafruit MagTag
'''

import time
import ssl
import json
import math
import wifi
import alarm
import board
import socketpool
import microcontroller
import adafruit_requests
from adafruit_magtag.magtag import MagTag

# Writes weather data to the screen
def set_weather_data(place_name, date, temperature, wind_chill, skies):
    magtag.set_text(
        "\n" + str(place_name) + " (" + str(date) +
        ")\nWeather: " + str(temperature) +
        " C\nWind Chill: " + str(wind_chill) +
        " C\nSkies: " + str(skies)
    )

# Puts the device to a deep sleep
def sleep_device():
    # Sleep until the alarm goes off (if button D11 is pressed or after 3600 seconds (1 hour))
    magtag.peripherals.deinit()
    pin_alarm = alarm.pin.PinAlarm(pin=board.D11, value=False, pull=True)
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 3600)
    alarm.exit_and_deep_sleep_until_alarms(pin_alarm, time_alarm)

# Add text display
magtag = MagTag()

# Disabling unused features for battery saving
magtag.peripherals.speaker_disable = True

# Import Network SSH
from secrets import secrets

# Attempt to connect to Wi-Fi
try:
    # Set text formatting
    magtag.add_text(
        text_position=(
                1,
                (magtag.graphics.display.height // 2) - 25,
            ),
            text_scale=1.5,
    )
    # Turn LEDS on and set the colour to blue
    magtag.peripherals.neopixels.brightness = 0.1
    magtag.peripherals.neopixels.fill((0, 0, 255))
    # Set text to the screen 
    magtag.set_text("\nConnecting to " + secrets["ssid"] + "...")
    # Connect to Wi-Fi
    wifi.radio.connect(secrets["ssid"], secrets["password"])
except:
    # Set the colour of the LEDs to red
    magtag.peripherals.neopixels.fill((255, 0, 0))
    magtag.set_text("\nError connecting to\n" + secrets["ssid"] + ".\nRestarting in 10 seconds.")
    # Wait 10 seconds
    time.sleep(10)
    # Reset program
    microcontroller.reset()
else:
    print("Successfly connected to " + secrets["ssid"] + ".")
    print("IP address: ", wifi.radio.ipv4_address)

# Get Mount Tremblant Weather JSON file
try:
    # Set the colour of the LEDs to purple
    magtag.peripherals.neopixels.fill((255, 0, 255))
    magtag.set_text("\nObtaining information...")
    # Begin request
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    # Request file
    MOUNTAIN_URL = "https://mtnpowder.com/feed?resortId=4"
    mountain_info = requests.get(MOUNTAIN_URL)
    # Get Current Weather information
    current_temp = math.ceil(float(mountain_info.json()["CurrentConditions"]["Base"]["TemperatureC"]))
    current_chill = math.ceil(float(mountain_info.json()["CurrentConditions"]["Base"]["WindChillC"]))
    current_skies = mountain_info.json()["CurrentConditions"]["Base"]["Skies"]
    current_date = mountain_info.json()["Forecast"]["OneDay"]["date"]
except:
    magtag.peripherals.neopixels.fill((255, 0, 0))
    magtag.set_text("\nError obtaining the weather.\nRestarting in 10 seconds.")
    time.sleep(10)
    microcontroller.reset()

# Set the colour of the LEDs to green
magtag.peripherals.neopixels.fill((0, 255, 0))

'''
# Prompt to select a day to request
timer = 5
day_requesting = 0
while timer != 0:
    # Set the colour of the LEDs to yellow
    magtag.peripherals.neopixels.fill((255, 255, 0))
    button_D14_pressed = magtag.peripherals.button_b_pressed
    button_D12_pressed = magtag.peripherals.button_c_pressed

    # Change the day being requested if a button is pressed
    if button_D14_pressed == True:
        day_requesting = day_requesting + 1
    elif button_D12_pressed == True:
        day_requesting = day_requesting - 1
    magtag.set_text(
        "\nDay Requesting: " + str(day_requesting) + "\n" +
        "Time until request: " + str(timer)
    )
    time.sleep(1)
    timer = timer - 1
'''

# Add text on screen
set_weather_data(
    "Village",
    current_date,
    current_temp,
    current_chill,
    current_skies
)

# Sleep after 15 seconds
time.sleep(15)
sleep_device()
