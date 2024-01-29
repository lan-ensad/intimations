##################
# SENSOR PINMAP
# index   0   1   2   3   4   5     6       7
# echo    0   2   4   7  10   12    14      17
# trig    1   3   5   8  11   13    15      16
##################

from sr04 import HCSR04
import network
import machine
import time

SHIELD = "sensors"

# ### BLINK STATE ###
led = machine.Pin("LED", machine.Pin.OUT)
timerb = machine.Timer()
def blink(timer):
    led.toggle()
timerb.init(period=200, mode=machine.Timer.PERIODIC, callback=blink)

print(f"=== Shield : {SHIELD} ===")

# ### NETWORK ###
count = 0
to = 30
ssid = '<SSID>'
password = '<PASSWORD>'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print(f"Try connect to SSID : {ssid}")
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        if count>=to:
            machine.reset()
        time.sleep_ms(1000)
        count +=1
        print('.', end = " ")
        print(count)
if wlan.isconnected():
    timerb.deinit()
    time.sleep(1)
    print(f">> Connected on <{ssid}> with <{network.WLAN(network.STA_IF).ifconfig()[0]}>")