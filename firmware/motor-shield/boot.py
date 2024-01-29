# ##################
# MOTOR DRIVER PINMAP
#   0       1       2       3
# PWM 0   PWM 2   PWM 4   PWM 6
# PH  1   PH  3   PH  5   PH  7
# ##################
# ENDSTOP PINMAP
#   0       1       2       3
# SIG 21  SIG 20  SIG 19  SIG 18
# ##################

import network
import machine
import time

SHIELD = "Motors"

# ### BLINK STATE ###
led = machine.Pin("LED", machine.Pin.OUT)
timerb = machine.Timer()
def blink(timer):
    led.toggle()
timerb.init(period=150, mode=machine.Timer.PERIODIC, callback=blink)

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
    print(f">> Connected on <{ssid}> with <{network.WLAN(network.STA_IF).ifconfig()[0]}>")