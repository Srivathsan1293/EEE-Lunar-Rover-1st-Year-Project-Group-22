import paho.mqtt.client as mqtt
import serial
import keyboard
import time
import json
mqttBroker = "localhost"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(host = 'localhost', port = 1883)

while True:
    client.publish("sensor_read",json.dumps({ "s1": "hi", "s2": "1", "s3": "hi", "s4": "hi","rock" : "Basaltoid" }))
    time.sleep(1)

