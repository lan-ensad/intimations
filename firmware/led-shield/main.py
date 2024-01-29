from neopixel import Neopixel
from umqttsimple import MQTTClient
import ubinascii
import machine
import time
import json

# ### BLINK STATE ###
led = machine.Pin("LED", machine.Pin.OUT)
timer = machine.Timer()
def blink(timer):
    led.toggle()
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=blink)

# ### MQTT ###
SERVER = '<MQTT SERVER IP>'
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
mqttClient = MQTTClient(CLIENT_ID, SERVER)
mqttClient.connect()

# ### COLORS ###
cold_white=(225, 225, 225)
warm_white=(245, 175, 100)
red = (255, 10, 0)
orange = (200, 50, 0)
yellow = (200, 175, 0)
green = (5, 225, 5)
blue = (10, 10, 225)
violet = (100, 0, 90)
rgbAll = [cold_white, warm_white, red, orange, yellow, green, blue, violet]

brightnessFader=[0, 0, 0, 0]
faderAmount=[0, 0, 0, 0]
strips = [
    Neopixel(num_leds=45, state_machine=3, pin=3, mode='GRB'),
    Neopixel(num_leds=91, state_machine=7, pin=7, mode='GRB'),
    Neopixel(num_leds=134, state_machine=0, pin=11, mode='GRB'),
    Neopixel(num_leds=178, state_machine=1, pin=15, mode='GRB')
]
##      LED SECTORS
##  A,B,C,D : 0→full ring ++
## A→3    B→3   C→5     D→5
ledsectors=[
    [
        [0, 45],
        [0, 15],
        [12,35],
        [28, 45]
    ],
    [
        [0, 91],
        [0, 35],
        [18, 55],
        [50, 91]
    ],
    [
        [0,134],
        [0,65],
        [35,91],
        [53,101],
        [23,71],
        [92,134]
    ],
    [
        [0,178],
        [0,42],
        [23,59],
        [47,91],
        [81,117],
        [111,178],
    ]
]
# ### STRIP FUNCTIONS ###
def allColor(strip, t, bright):
    count = 0
    while True:
        if count>=len(rgbAll):
            count = 0
        strips[strip].clear()
        strips[strip].fill(rgbAll[count], bright)
        strips[strip].show()
        print(rgbAll[count])
        time.sleep(t)
        count +=1
def fillOne(strip, col, bright):
    strips[strip].clear()
    strips[strip].brightness(bright)
    strips[strip].fill(rgbAll[col])
    strips[strip].show()
def resetAll():
    for i in range(4):
        strips[i].clear()
        strips[i].show()
def resetOne(strip):
    global brightnessFader
    brightnessFader[strip]=0
    for i in range(strips[strip].num_leds):
        strips[strip].clear()
        strips[strip].show()
def segOneFix(strip, start, end, col, bright):
    resetOne(strip)
    strips[strip].brightness(bright)
    for i in range(start, end):
        strips[strip].set_pixel(i, rgbAll[col])
        strips[strip].show()
def snaking(strip, t):
    while True:
        for i in range(strips[strip].num_leds):
            strips[strip].clear()
            strips[strip].set_pixel(i, orange, 50)
            strips[strip].show()
            time.sleep(t)
def segOneFade(strip, start, end, tick, amount, col):
    global brightnessFader
    global faderAmount
    brightnessFader[strip]=0
    faderAmount[strip]=amount
    while True:
        brightnessFader[strip]+=faderAmount[strip]
        if brightnessFader[strip]>=200 or brightnessFader[strip]<=0:
            faderAmount[strip]*=-1
        strips[strip].brightness(brightnessFader[strip])
        for i in range(start, end):
            strips[strip].set_pixel(i, rgbAll[col])
            strips[strip].show()
            time.sleep_ms(tick)


# ### MAIN CALLBACK ###
def sub_cb(topic, msg):
    # ###  PARSE JSON  ###
    data = ""
    for i in msg:
        data += chr(i)
    data_j = json.loads(data)
    index = int(data_j.get('index')['payload'])
    colour = int(data_j.get('color')['payload'])
    sector = int(data_j.get('sector')['payload'])
    brightness= int(data_j.get('brightness')['payload'])
    if brightness <= 1:
        resetOne(index)
        print(f'reset strip n°{index}')
    else:
        segOneFix(index, ledsectors[index][sector][0], ledsectors[index][sector][1], colour, brightness)
        print(f'strip : {index} on sector : {sector} : {rgbAll[colour]} at {brightness}')

TOPIC = "leds"
mqttClient.set_callback(sub_cb)
mqttClient.subscribe(TOPIC)
print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))

def main():
    while True:
        mqttClient.check_msg()

if __name__ == "__main__":
    main()