from sr04 import HCSR04
from umqttsimple import MQTTClient
import ubinascii
import time
import machine
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
#===  PUBLISHER  ===
def publishTimer(timer):
    pubTopic = 'sensors'
    pubData = sensorsValue()
    mqttClient.publish(pubTopic, str(pubData).encode())
    print(f"Publishing topic :<{pubTopic}> | data :<{pubData}>")
sendTimer = machine.Timer()
sendTimerRange = 5000


# ### SENSORS ###
TIMEOUT = 150000
sensors=[
    HCSR04(0, 1, TIMEOUT),
    HCSR04(2, 3, TIMEOUT),
    HCSR04(4, 5, TIMEOUT),
    HCSR04(7, 8, TIMEOUT),
    HCSR04(10, 11, TIMEOUT),
    HCSR04(12, 13, TIMEOUT)
]
distance=[0, 1, 2, 3, 4, 5]
#===  READ SENSORS  ===
def sensorsValue():
    msg = ""
    for i in range(6):
        distance[i]=sensors[i].distance_mm()
    msg = '{"s00":'+str(distance[0])+',"s01":'+str(distance[1])+',"s02":'+str(distance[2])+',"s03":'+str(distance[3])+',"s04":'+str(distance[4])+',"s05":'+str(distance[5])+'}'
    return msg

### MAIN CALLBACK ###
def sub_cb(topic, msg):
    data = ""
    for i in msg:
        data+=chr(i)
    data_j = json.loads(data)
    if data_j == True:
        sendTimer.init(period=sendTimerRange, mode=machine.Timer.PERIODIC, callback=publishTimer)
        pass
    elif data_j==False:
        sendTimer.deinit()
        pass
    print(data_j)

### SET SUB ###
TOPIC = "read"
mqttClient.set_callback(sub_cb)
mqttClient.subscribe(TOPIC)
print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))
def main():
    while True:
        mqttClient.check_msg()

if __name__ == "__main__":
    main()
