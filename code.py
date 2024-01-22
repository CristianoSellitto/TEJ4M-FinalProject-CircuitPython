'''
- Created By Cristiano Sellitto
- Created December 12th 2023
- Modified January 2024

This program writes the current or future weather information in Mont Tremblant to an Adafruit MagTag
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

# Reduce the brightness of the LEDs as a way to see when a timer is about to run out
def led_brightness_timer(timer):
    if timer == 1500: # Can't use match case for this due to older Python version (probably)
        magtag.peripherals.neopixels.brightness = 0.3
    elif timer == 1350:
        magtag.peripherals.neopixels.brightness = 0.275
    elif timer == 1350:
        magtag.peripherals.neopixels.brightness = 0.25
    elif timer == 1200:
        magtag.peripherals.neopixels.brightness = 0.225
    elif timer == 1050:
        magtag.peripherals.neopixels.brightness = 0.2
    elif timer == 900:
        magtag.peripherals.neopixels.brightness = 0.175
    elif timer == 750:
        magtag.peripherals.neopixels.brightness = 0.15
    elif timer == 600:
        magtag.peripherals.neopixels.brightness = 0.125
    elif timer == 450:
        magtag.peripherals.neopixels.brightness = 0.1
    elif timer == 300:
        magtag.peripherals.neopixels.brightness = 0.05
    elif timer == 150:
        magtag.peripherals.neopixels.brightness = 0.01

# Select a day's weather data to request
def select_day(timer, selected_day):
    # Get Tremblant Weather JSON file
    try:
        # Prompt the device to select a day to request
        magtag.set_text(
            "\nPress up or down to" + 
            "\nselect a day." + 
            "\nPress left to continue." + 
            "\nDay Requesting: +" + str(selected_day)
        )
        while True:
            # Button variables
            button_D15_pressed = magtag.peripherals.button_a_pressed # Left button
            button_D14_pressed = magtag.peripherals.button_b_pressed # Up button
            button_D12_pressed = magtag.peripherals.button_c_pressed # Down button

            # Set the colour of the LEDs to yellow
            magtag.peripherals.neopixels.fill((255, 255, 0))

            # Change the brightness of the LEDs depending on what the timer is
            led_brightness_timer(timer)

            # Change the day being requested if a button is pressed
            if button_D15_pressed or timer == 0:
                # End loop if the left button is pressed or after 15 seconds
                break
            elif button_D14_pressed == True and selected_day < 4:
                # Add one day to request if the day being requested is less than 4
                selected_day = selected_day + 1
                magtag.set_text("\nDay Requesting: +" + str(selected_day))
            elif button_D12_pressed == True and selected_day > 0:
                # Subtract one day to request if the day being requested is greater than 0
                selected_day = selected_day - 1
                magtag.set_text("\nDay Requesting: +" + str(selected_day))
            # Print the time remaining to the console
            timer = timer - 1
            print(timer)
            time.sleep(0.01) # Number of seconds needed to wait is equal to timer x 0.01
        # Return the selected day
        return selected_day
    except:
        magtag.peripherals.neopixels.fill((255, 0, 0))
        magtag.set_text("\nError requesting the\nweather.\nRestarting in 10 seconds.")
        time.sleep(10)
        microcontroller.reset()

# Requests a JSON file from a URL
def get_json_url(mountain_url):
    # Set the colour of the LEDs to light blue
    magtag.peripherals.neopixels.brightness = 0.3
    magtag.peripherals.neopixels.fill((0, 255, 255))
    # Begin request
    magtag.set_text("\nRequesting weather\ndata...")
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    # Request the JSON file from the API
    mountain_info = requests.get(mountain_url)
    # Return the JSON file
    return mountain_info

# Get Tremblant Weather information
def request_weather_data(selected_day, page, json_file, is_first_request):
    # Set the colour of the LEDs to purple
    magtag.peripherals.neopixels.brightness = 0.3
    magtag.peripherals.neopixels.fill((255, 0, 255))
    if selected_day == 0:
        # Request weather information for the current day
        if is_first_request == True:
            # Only show the request text if this request is the first one, as the first request is slow
            magtag.set_text("\nRetrieving the weather\nfor today (Page " + str(page + 1) + ")...")
        if page == 0:
            # Request today's weather info for page 0
            weather_info = [
                True,
                json_file.json()["Forecast"]["OneDay"]["date"],
                math.ceil(float(json_file.json()["CurrentConditions"]["Base"]["TemperatureC"])),
                math.ceil(float(json_file.json()["CurrentConditions"]["Base"]["WindChillC"])),
                json_file.json()["CurrentConditions"]["Base"]["Skies"],
                None,
                None,
                json_file.json()["OperatingStatus"]
            ]
        elif page == 1:
            # Request today's weather info for page 1
            weather_info = [
                True,
                json_file.json()["Forecast"]["OneDay"]["date"],
                json_file.json()["SnowReport"]["TotalOpenTrails"],
                json_file.json()["SnowReport"]["TotalTrails"],
                json_file.json()["SnowReport"]["TotalOpenLifts"],
                json_file.json()["SnowReport"]["TotalLifts"],
                math.floor(
                    (
                        float(json_file.json()["SnowReport"]["OpenTerrainHectares"]) /
                        float(json_file.json()["SnowReport"]["TotalTerrainHectares"])
                    ) * 100
                ),
                json_file.json()["OperatingStatus"]
            ]
        elif page == 2:
            # Request today's weather info for page 2
            weather_info = [
                True,
                json_file.json()["Forecast"]["OneDay"]["date"],
                json_file.json()["SnowReport"]["TotalOpenParks"],
                json_file.json()["SnowReport"]["TotalParks"],
                json_file.json()["SnowReport"]["SeasonTotalCm"],
                json_file.json()["SnowReport"]["BaseArea"]["Last24HoursCm"],
                None,
                json_file.json()["OperatingStatus"]
            ]
    else:
        # Request weather information for a day in the future
        if is_first_request == True:
            magtag.set_text(
                "\nRetrieving the weather\nfor " +
                str(selected_day) + " day(s) in the\nfuture (Page " + str(page + 1) + ")..."
            )
        if selected_day == 1:
            day_text = "TwoDay"
        elif selected_day == 2:
            day_text = "ThreeDay"
        elif selected_day == 3:
            day_text = "FourDay"
        elif selected_day == 4:
            day_text = "FiveDay"
        if page == 0:
            # Request future weather info for page 0
            weather_info = [
                False,
                json_file.json()["Forecast"][day_text]["date"],
                math.ceil(float(json_file.json()["Forecast"][day_text]["temp_high_c"])),
                math.ceil(float(json_file.json()["Forecast"][day_text]["temp_low_c"])),
                json_file.json()["Forecast"][day_text]["skies"],
                None,
                None,
                json_file.json()["OperatingStatus"]
            ]
        elif page == 1:
            # Request future weather info for page 1
            weather_info = [
                False,
                json_file.json()["Forecast"][day_text]["date"],
                json_file.json()["Forecast"][day_text]["forecasted_snow_cm"],
                json_file.json()["Forecast"][day_text]["avewind"]["kph"],
                json_file.json()["Forecast"][day_text]["avewind"]["dir"],
                None,
                None,
                json_file.json()["OperatingStatus"]
            ]
    
    # Return the weather data requested
    return weather_info

# Writes the requested weather data to the screen
def set_weather_data(page, is_current_day, date, data_one, data_two, data_three, data_four, data_five):
    # Set the colour of the LEDs to green
    magtag.peripherals.neopixels.fill((0, 255, 0))
    '''
    - Page and Weather Data Information -

    Pages display different pieces of the total weather data for a day as strings
    Pages are always shown on the display as one page higher 

    weather_info[0] = is_current_day
    weather_info[1] = date
    weather_info[2] = data_one
    weather_info[3] = data_two
    weather_info[4] = data_three
    weather_info[5] = data_four
    weather_info[6] = data_five
    weather_info[7] = Operating Status (unused in this function)

    Formatted as {today} | {future} or {all}
    Ex. data_one = One | Two
        data_two = Three
    One is info for today and Two is info for future days, while Three is info for all days

    All Pages:
        page = Requested Page Number
        date = Full Date as YYYY-MM-DD
        is_current_day = Is the day requested today? (bool)

    Page 0:
        data_one = Weather    | High
        data_two = Wind Chill | Low
        data_three = Sky Condition

    Page 1:
        data_one = Total Open Trails     | Forecasted Snowfall (cm)
        data_two = Total Trails          | Wind Speed (km/h)
        data_three = Total Open Lifts    | Wind Direction
        data_four = Open Lifts           | None
        data_five = Open Terrain Percent | None

    Page 2:
        data_one = Total Open Parks                | Non-existent
        data_two = Total Parks                     | Non-existent
        data_three = Season Total Snow (cm)        | Non-existent
        data_four = Snow in the Last 24 Hours (cm) | Non-existent
    '''

    # Page 2 for today
    if page == 2 and is_current_day == True:
        magtag.set_text(
            "\nPage " + str(page + 1) + " for " + str(date) +
            "\nParks: " + str(data_one) + "/" + str(data_two) +
            "\nSeason Total: " + str(data_three) + " cm" +
            "\n24 Hour: " + str(data_four) + " cm"
        )
    # Page 1 for today
    elif page == 1 and is_current_day == True:
        magtag.set_text(
            "\nPage " + str(page + 1) + " for " + str(date) +
            "\nTrails: " + str(data_one) + "/" + str(data_two) +
            "\nLifts: " + str(data_three) + "/" + str(data_four) +
            "\nOpen Terrain: " + str(data_five) + "%"
        )
    # Page 1 for future days
    elif page == 1 and is_current_day == False:
        magtag.set_text(
            "\nPage " + str(page + 1) + " for " + str(date) +
            "\nSnowfall: " + str(data_one) + " cm" +
            "\nWind Speed: " + str(data_two) +
            "\nWind Direction: " + str(data_three)
        )
    # Page 0 for today
    elif page == 0 and is_current_day == True:
        magtag.set_text(
            "\nPage " + str(page + 1) + " for " + str(date) +
            "\nWeather: " + str(data_one) +
            " C\nWind Chill: " + str(data_two) +
            " C\n" + str(data_three)
        )
    # Page 0 for future days (default)
    else:
        magtag.set_text(
            "\nPage " + str(page + 1) + " for " + str(date) +
            "\nHigh: " + str(data_one) +
            " C\nLow: " + str(data_two) +
            " C\n" + str(data_three)
        )

# Puts the device into a deep sleep
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

# Import network information from secrets.py
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
    magtag.peripherals.neopixels.brightness = 0.3
    magtag.peripherals.neopixels.fill((0, 0, 255))
    # Set text to the screen 
    magtag.set_text("\nConnecting to\n" + secrets["ssid"] + "...")
    # Connect to Wi-Fi
    wifi.radio.connect(secrets["ssid"], secrets["password"])
except:
    # Set the colour of the LEDs to red
    magtag.peripherals.neopixels.fill((255, 0, 0))
    magtag.set_text("\nError connecting to\n" + secrets["ssid"] + ".\nRestarting in 10 seconds.")
    # Wait for 10 seconds
    time.sleep(10)
    # Reset program
    microcontroller.reset()
else:
    # Print IP information to console
    print("Successfully connected to " + secrets["ssid"] + ".")
    print("IP address: ", wifi.radio.ipv4_address)

try:
    # Get the mountain's weather JSON
    mountain_json = get_json_url("https://mtnpowder.com/feed?resortId=4")
    # Select a day to request
    requested_day = select_day(1500, 0)
    # Request page 0's weather data for the requested day
    current_page = 0
    weather_data = request_weather_data(requested_day, current_page, mountain_json, True)
except:
    magtag.peripherals.neopixels.fill((255, 0, 0))
    magtag.set_text("\nError requesting the\nweather information.\nRestarting in 10 seconds.")
    time.sleep(10)
    microcontroller.reset()

# Write Tremblant's operating status to the screen
magtag.peripherals.neopixels.fill((0, 255, 0))
magtag.set_text("\nTremblant Status: " + weather_data[7])
time.sleep(5)

# Write the weather data to the screen
set_weather_data(
    current_page,
    weather_data[0],
    weather_data[1],
    weather_data[2],
    weather_data[3],
    weather_data[4],
    weather_data[5],
    weather_data[6]
)

# Check when buttons are pressed, and turn off if no inputs are read for a while
timer = 1500
while True:
    # Button variable
    button_D15_pressed = magtag.peripherals.button_a_pressed # Left button
    button_D14_pressed = magtag.peripherals.button_b_pressed # Up button
    button_D12_pressed = magtag.peripherals.button_c_pressed # Down button

    led_brightness_timer(timer)

    if timer == 0:
        # Put the device to sleep when timer runs out
        sleep_device()
    elif button_D15_pressed == True:
        # Request a weather data change if the left button is pressed
        requested_day = select_day(1500, requested_day)
        # If the current page is 2 and the requested day isn't today, set the page to 1 
        if current_page == 2 and requested_day != 0:
            current_page = 1
        weather_data = request_weather_data(requested_day, current_page, mountain_json, False)
        set_weather_data(
            current_page,
            weather_data[0],
            weather_data[1],
            weather_data[2],
            weather_data[3],
            weather_data[4],
            weather_data[5],
            weather_data[6]
        )
        # Restart timer
        timer = 1500
    elif button_D14_pressed and current_page < 2 and not (current_page == 1 and requested_day != 0):
        # Request a higher page if...
        # The current page is less than 2 and not 1 if the requested day isn't today
        current_page = current_page + 1
        weather_data = request_weather_data(requested_day, current_page, mountain_json, False)
        set_weather_data(
            current_page,
            weather_data[0],
            weather_data[1],
            weather_data[2],
            weather_data[3],
            weather_data[4],
            weather_data[5],
            weather_data[6]
        )
        timer = 1500
    elif button_D12_pressed and current_page > 0:
        # Request a lower page if the current page is more than 0
        current_page = current_page - 1
        weather_data = request_weather_data(requested_day, current_page, mountain_json, False)
        set_weather_data(
            current_page,
            weather_data[0],
            weather_data[1],
            weather_data[2],
            weather_data[3],
            weather_data[4],
            weather_data[5],
            weather_data[6]
        )
        timer = 1500

    timer = timer - 1
    time.sleep(0.01)
