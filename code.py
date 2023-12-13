import time
import ssl
import alarm
import board
import socketpool
import wifi
import adafruit_requests
import json
from adafruit_magtag.magtag import MagTag

# Add text display
magtag = MagTag()
magtag.add_text(
    text_position=(
        1,
        (magtag.graphics.display.height // 2) - 25,
    ),
    text_scale=1.5,
)
# Disabling unused features for battery saving
magtag.peripherals.neopixel_disable = False
magtag.peripherals.speaker_disable = True

# Network SSH
network_info = {
    'ssid' : 'Room212',
    'password' : 'temp',
}

# Connect to Wifi
print("Attempting to connect to " + network_info["ssid"] + "...")
wifi.radio.connect(network_info["ssid"], network_info["password"])
print("Successfly connected to " + network_info["ssid"] + ".")
print("IP address: ", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

MOUNTAIN_URL = "https://mtnpowder.com/feed?resortId=4"
mountain_info = requests.get(MOUNTAIN_URL)

current_temp = mountain_info.json()["CurrentConditions"]["Base"]["TemperatureC"]
current_skies = mountain_info.json()["CurrentConditions"]["Base"]["Skies"]
current_date = mountain_info.json()["Forecast"]["OneDay"]["date"]

# Add text on screen
magtag.set_text("\nWeather: " + current_temp + "ºC")
magtag.peripherals.neopixels.brightness = 0.1
magtag.peripherals.neopixels.fill((0, 255, 0))

while True:
    button_one = magtag.peripherals.button_a_pressed
    button_two = magtag.peripherals.button_b_pressed

    if button_one == True:
        magtag.set_text("\nSleep")
        # Sleep until the alarm goes off (if button D11 is pressed or after 300 seconds (5 minutes))
        magtag.peripherals.deinit()
        pin_alarm = alarm.pin.PinAlarm(pin=board.D11, value=False, pull=True)
        time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 300)
        alarm.exit_and_deep_sleep_until_alarms(pin_alarm, time_alarm)
    elif button_two == True:
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
