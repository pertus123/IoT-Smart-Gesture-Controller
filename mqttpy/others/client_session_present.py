#!/usr/bin/python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt


def on_connect(mqttc, obj, flags, rc):
    if obj == 0:
        print("First connection:")
    elif obj == 1:
        print("Second connection:")
    elif obj == 2:
        print("Third connection (with clean session=True):")
    print("    Session present: " + str(flags['session present']))
    print("    Connection result: " + str(rc))
    mqttc.disconnect()


def on_disconnect(mqttc, obj, rc):
    mqttc.user_data_set(obj + 1)
    if obj == 0:
        mqttc.reconnect()


def on_log(mqttc, obj, level, string):
    print(string)


mqttc = mqtt.Client(client_id="asdfj", clean_session=False)
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqttc.user_data_set(0)
mqttc.connect("localhost", 1883)
mqttc.loop_forever()

# Clear session
mqttc = mqtt.Client(client_id="asdfj", clean_session=True)
mqttc.on_connect = on_connect
mqttc.user_data_set(2)
mqttc.connect("localhost", 1883)
mqttc.loop_forever()