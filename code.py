'''
- By Cristiano
- Created December 12th 2023
- Modified January 2024

This program writes the current or future weather information in Mont Tremblant to a Adafruit MagTag
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

# Writes the requested weather data to the screen
def set_weather_data(place_name, temperature, wind_chill, skies, date, is_current_day):
    # If the requested day is today...
    if is_current_day == True:
        magtag.set_text(
            "\n" + str(place_name) + " on " + str(date) +
            "\nWeather: " + str(temperature) +
            " C\nWind Chill: " + str(wind_chill) +
            " C\n" + str(skies)
        )
    # If the requested day is in the future...
    else:
        magtag.set_text(
            "\n" + str(place_name) + " on " + str(date) +
            "\nHigh: " + str(temperature) +
            " C\nLow: " + str(wind_chill) +
            " C\n" + str(skies)
        )

# Puts the device into the deep sleep mode
def sleep_device():
    # Sleep until an alarm goes off (if button D11 (right button) is pressed or after 3600 seconds (1 hour))
    magtag.peripherals.deinit()
    pin_alarm = alarm.pin.PinAlarm(pin=board.D11, value=False, pull=True)
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 3600)
    alarm.exit_and_deep_sleep_until_alarms(pin_alarm, time_alarm)

# Add MagTag library
magtag = MagTag()

# Disable unused features for battery saving
magtag.peripherals.speaker_disable = True

# Import Network SSH from secrets.py
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
    magtag.set_text("\nConnecting to\n" + secrets["ssid"] + "...")
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
    magtag.set_text("\nDownloading weather\ndata...")
    # Begin request
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    # Request the JSON file from the API
    MOUNTAIN_URL = "https://mtnpowder.com/feed?resortId=4"
    mountain_info = requests.get(MOUNTAIN_URL)
    # Prompt the device to select a day to request
    timer = 1500
    day_requesting = 0
    magtag.set_text("\nPress up or down to\nselect a day.\nPress left to continue.")
    while True:
        # Button variables
        button_D15_pressed = magtag.peripherals.button_a_pressed # Left button
        button_D14_pressed = magtag.peripherals.button_b_pressed # Up button
        button_D12_pressed = magtag.peripherals.button_c_pressed # Down button

        # Set the colour of the LEDs to yellow
        magtag.peripherals.neopixels.fill((255, 255, 0))

        # Change the day being requested if a button is pressed
        if button_D15_pressed or timer == 0:
            # End loop if the left button is pressed or after 15 seconds
            break
        elif button_D14_pressed == True and day_requesting < 4:
            # Add one day to request if the day being requested is less than 4
            day_requesting = day_requesting + 1
            magtag.set_text("\nDay Requesting: +" + str(day_requesting))
        elif button_D12_pressed == True and day_requesting > 0:
            # Subtract one day to request if the day being requested is greater than 0
            day_requesting = day_requesting - 1
            magtag.set_text("\nDay Requesting: +" + str(day_requesting))
        # Reduce the brightness of the timer as a way to see when time is about to run out
        timer = timer - 1
        magtag.peripherals.neopixels.brightness = timer / 100
        # Print the time remaining to the console
        print(timer)
        time.sleep(0.01)
    '''
    - weather_info Array Values -

    weather_info[0] = Temperature      (if weatherinfo[4] == True)
    weather_info[0] = High Temperature (if weatherinfo[4] == False)
    weather_info[1] = Wind Chill       (if weatherinfo[4] == True)
    weather_info[1] = Low Temperature  (if weatherinfo[4] == False)
    weather_info[2] = Sky Condition
    weather_info[3] = Full Date        (YYYY-MM-DD)
    weather_info[4] = Is the day being requested today?
    '''
    magtag.peripherals.neopixels.brightness = 0.1
    magtag.peripherals.neopixels.fill((0, 255, 255))
    if day_requesting == 0:
        # Request weather information for the current day
        magtag.set_text("\nRequesting the weather\nfor today...")
        weather_info = [
            math.ceil(float(mountain_info.json()["CurrentConditions"]["Base"]["TemperatureC"])),
            math.ceil(float(mountain_info.json()["CurrentConditions"]["Base"]["WindChillC"])),
            mountain_info.json()["CurrentConditions"]["Base"]["Skies"],
            mountain_info.json()["Forecast"]["OneDay"]["date"],
            True
        ]
    else:
        # Request weather information for a day in the future
        magtag.set_text(
            "\nRequesting the weather\nfor " + str(day_requesting) + " day(s) in the\nfuture...")
        if day_requesting == 1: # Can't use match case for this due to older Python version
            day_text = "TwoDay"
        elif day_requesting == 2:
            day_text = "ThreeDay"
        elif day_requesting == 3:
            day_text = "FourDay"
        elif day_requesting == 4:
            day_text = "FiveDay"
        weather_info = [
            math.ceil(float(mountain_info.json()["Forecast"][day_text]["temp_high_c"])),
            math.ceil(float(mountain_info.json()["Forecast"][day_text]["temp_low_c"])),
            mountain_info.json()["Forecast"][day_text]["skies"],
            mountain_info.json()["Forecast"][day_text]["date"],
            False
        ]
except:
    magtag.peripherals.neopixels.fill((255, 0, 0))
    magtag.set_text("\nError obtaining the\nweather.\nRestarting in 10 seconds.")
    time.sleep(10)
    microcontroller.reset()

# Set the colour of the LEDs to green
magtag.peripherals.neopixels.fill((0, 255, 0))

# Put the weather data on the screen
set_weather_data(
    "Village",
    weather_info[0],
    weather_info[1],
    weather_info[2],
    weather_info[3],
    weather_info[4]
)

# Sleep after 15 seconds
time.sleep(15)
sleep_device()
