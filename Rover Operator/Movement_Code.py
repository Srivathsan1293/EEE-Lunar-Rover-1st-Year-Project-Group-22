import paho.mqtt.client as mqtt
import serial
import keyboard
import time
mqttBroker = "localhost"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(host = 'localhost', port = 1883)

msg = "stop"

while True:
    client.loop_start()
    if keyboard.is_pressed('w'):
        if msg != "w":
            client.publish('movement_controls',"11255255")
            msg = "w"
        print('w')
    elif keyboard.is_pressed('s'):
        if msg != "s":
            msg = "s"
            client.publish('movement_controls','00255255')
        print('s')
    elif keyboard.is_pressed('d'):
        if msg != "d":
            msg = "d"
            client.publish('movement_controls','01255255')
        print('d')
    elif keyboard.is_pressed('a'):
        if msg != "a":
            msg = "a"
            client.publish('movement_controls','10255255')
        print('a')
    else:
        if msg != "stop":
            msg = "stop"
            client.publish('movement_controls', '0000000')
        print('stop')


