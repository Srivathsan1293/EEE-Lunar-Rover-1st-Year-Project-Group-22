import paho.mqtt.client as mqtt
import serial
import keyboard
import time
import json
mqttBroker = "localhost"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(host = 'localhost', port = 1883)

while True:
    client.publish("rover/sensors",json.dumps({ "s1": 23.451, "s2": "1", "s3": 0.734, "s4": 12.100,"rock" : "Basaltoid" }))
    time.sleep(1)
    client.publish("rover/sensors",json.dumps({ "s1": 3543, "s2": "0", "s3": 0.345, "s4": 1.100,"rock" : "Regolix" }))
    time.sleep(1)
