import paho.mqtt.client as mqtt
import subscriber as sb
import publisher as pb
import matplotlib.pyplot as mat
from time import time, sleep

# Initialize of MQTT Protocol
broker_url = "54.180.101.122"
# broker_url = "localhost"
broker_port = 1883

client = mqtt.Client(client_id="play", clean_session=True, userdata=None)
client.on_connect = sb.on_connect

# To Process Every Other Message
client.on_message = sb.on_message

client.connect(broker_url, broker_port)
# client.on_message = on_message

# client.subscribe("TestingTopic", qos=1)
client.subscribe("test")
# client.subscribe("BedroomTopic", qos=1)
client.message_callback_add("test", sb.on_message_from_kitchen)
# client.message_callback_add("BedroomTopic", sb.on_message_from_bedroom)

client.loop_forever()


