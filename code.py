import time
import alarm
import board
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

# Add text on screen
magtag.set_text("\ntext")
magtag.peripherals.neopixels.brightness = 0.2
magtag.peripherals.neopixels.fill((0, 255, 0))

while True:
    button_one = magtag.peripherals.button_a_pressed
    button_two = magtag.peripherals.button_b_pressed

    if button_one == True:
        magtag.set_text("\nSleep")
        # Sleep until the alarm goes off (if button D11 is pressed or after 5 seconds)
        magtag.peripherals.deinit()
        pin_alarm = alarm.pin.PinAlarm(pin=board.D11, value=False, pull=True)
        time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 5)
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
