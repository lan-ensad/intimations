import machine
from umqttsimple import MQTTClient
import ubinascii
import time
from motor import Motor
import json

# ### BLINK STATE ###
led = machine.Pin("LED", machine.Pin.OUT)
ledState = machine.Timer()
def blink(timer):
    led.toggle()
ledState.init(period=1000, mode=machine.Timer.PERIODIC, callback=blink)

# ### MQTT ###
SERVER = '<MQTT SERVER IP>'
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
mqttClient = MQTTClient(CLIENT_ID, SERVER)
mqttClient.connect()

# ### MOTORS ###
motors = [
    Motor(0, 1),
    Motor(2, 3),
    Motor(4, 5),
    Motor(6, 7)
]
endstop = [
    machine.Pin(21, machine.Pin.IN),
    machine.Pin(20, machine.Pin.IN),
    machine.Pin(19, machine.Pin.IN),
    machine.Pin(18, machine.Pin.IN)
]
speedValTable=[0,0,0,0]
dirTable=[False, False, False, False]

def checkMotsTimer(timer):
    global speedValTable
    for i in range(4):
        motors[i].updateTimer(time.ticks_ms())
        if motors[i].timer>motors[i].duration and motors[i].targetSpeed!=0:
            print(f'motor {i} timeout')
            motors[i].Stop()
            speedValTable[i]=0
checkMotorsTimer=machine.Timer()
checkMotorsTimer.init(period=100, mode=machine.Timer.PERIODIC, callback=checkMotsTimer)

def All(direction, val):
    for i in range(4):
        motors[i].Turn(direction, val)

def StopAll():
    for i in range(4):
        motors[i].Stop()

# ### MAIN CALLBACK ###
def sub_cb(topic, msg):
    global speedValTable
    global dirTable
    # ###  PARSE JSON  ###
    data = ""
    index = ""
    for i in msg:
        data += chr(i)
    data_j = json.loads(data)
    index = int(data_j.get('index')['payload'])
    if 'stop' in data_j:
        motors[index].Stop()
        speedValTable[index]=0
    else:
        speedValTable[index]=int(data_j.get('speed')['payload'])
        dirTable[index]=data_j.get('dir')['payload']
        duration = int(data_j.get('time')['payload'])
        if motors[index].actualSpeed==0:
            motors[index].Turn(dirTable[index], speedValTable[index], time.ticks_ms())
            motors[index].setDuration(duration)
            print(f'motor {index} go at {speedValTable[index]}% during {duration}')

    # ###  PRINT TABLES  ###
    for i in range(4):
        print(dirTable[i], end=':')
        print(speedValTable[i], end=' | ')
    print('')

TOPIC = "motors"
mqttClient.set_callback(sub_cb)
mqttClient.subscribe(TOPIC)
print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))

def main():
    while True:
        mqttClient.check_msg()

if __name__ == "__main__":
    main()