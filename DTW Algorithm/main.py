import paho.mqtt.client as mqtt
#import serial
from numpy import *
import matplotlib.pyplot as plt
from matplotlib import animation
import subscriber as sb
import publisher as pb
import matplotlib.pyplot as mat
#from time import time, sleep
import time
import json
import testtt

# Initialize of MQTT Protocol
broker_url = "54.180.101.122"
broker_port = 1883
def on_connect(client,data,flag,rc):
    print("Connected",str(rc))
def on_message(client, userdata, message):
    test1 = str(message.payload.decode("utf-8"))
    jsonData = json.loads(test1)
    resultFlex = jsonData["Flex"]
    resultAcc = jsonData["Acc"]
    resultGy = jsonData["Gy"]
    print(resultFlex)
    print(resultAcc)
    print(resultGy)

client = mqtt.Client()

client.on_connect=on_connect
client.on_message = on_message
client.subscribe("test", qos=0)

client.connect(broker_url, broker_port)

client.loop_forever()