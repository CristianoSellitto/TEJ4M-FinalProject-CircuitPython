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

# Puts the device to a deep sleep
def sleep_device():
    # Sleep until the alarm goes off (if button D11 is pressed or after 3600 seconds (1 hour))
    magtag.peripherals.deinit()
    pin_alarm = alarm.pin.PinAlarm(pin=board.D11, value=False, pull=True)
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 3600)
    alarm.exit_and_deep_sleep_until_alarms(pin_alarm, time_alarm)

# Add text display
magtag = MagTag()

# Import Network SSH
from secrets import secrets

# Attempt to connect to Wi-Fi
try:
    # Set text formatting
    magtag.add_text(
        text_position=(
                1,
                (magtag.graphics.display.height // 2) - 20,
            ),
            text_scale=1,
    )
    # Turn LEDS on and set the colour to blue
    magtag.peripherals.neopixels.brightness = 0.1
    magtag.peripherals.neopixels.fill((0, 0, 255))
    # Set text to the screen 
    magtag.set_text("\nConnecting to " + secrets["ssid"] + "...")
    # Connect to Wi-Fi
    wifi.radio.connect(secrets["ssid"], secrets["password"])
except:
    magtag.peripherals.neopixels.fill((255, 0, 0))
    magtag.set_text("\nError connecting to " + secrets["ssid"] + ".\nRestarting in 10 seconds.")
    # Wait 10 seconds
    time.sleep(10)
    # Reset program
    microcontroller.reset()
else:
    print("Successfly connected to " + secrets["ssid"] + ".")
    print("IP address: ", wifi.radio.ipv4_address)

# Set text formatting
magtag.add_text(
    text_position=(
        1,
        (magtag.graphics.display.height // 2) - 25,
    ),
    text_scale=1.5,
)

# Disabling unused features for battery saving
magtag.peripherals.speaker_disable = True

# Begin HTTP request
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# Get Mount Tremblant Weather Information
try:
    MOUNTAIN_URL = "https://mtnpowder.com/feed?resortId=4"
    mountain_info = requests.get(MOUNTAIN_URL)
except:
    magtag.set_text("\nError getting weather information.\nRestarting in 10 seconds.")
    time.sleep(10)
    microcontroller.reset()
current_temp = math.ceil(float(mountain_info.json()["CurrentConditions"]["Base"]["TemperatureC"]))
current_chill = math.ceil(float(mountain_info.json()["CurrentConditions"]["Base"]["WindChillC"]))
current_skies = mountain_info.json()["CurrentConditions"]["Base"]["Skies"]
current_date = mountain_info.json()["Forecast"]["OneDay"]["date"]

# Add text on screen
magtag.refresh()
magtag.set_text(
    "\nVillage Info\nWeather: " + str(current_temp) +
    " C\nWind Chill: " + str(current_chill) +
    " C\nLast Update: " + str("date")
)

# Turn LEDS to green and sleep after 15 seconds
magtag.peripherals.neopixels.fill((0, 255, 0))
time.sleep(15)
sleep_device()

while True:
    button_one_pressed = magtag.peripherals.button_a_pressed

    if button_one_pressed == True:
        magtag.set_text("\nTest2\ntest2?")
    
    '''
    magtag.set_text("\ntest")
    time.sleep(1)
    magtag.set_text("\nTest2\ntest2?")
    time.sleep(1)
    magtag.set_text("\nTest3\ntest3\ntest3?")
    time.sleep(1)
    magtag.set_text("\nTest4\ntest4\ntest4\ntest4?")
    time.sleep(1)
    '''
