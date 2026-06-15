import paho.mqtt.client as mqtt
import serial
import keyboard
import time
mqttBroker = "localhost"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(host = 'localhost', port = 1883)
import pygame
import time

DEADZONE   = 0.08
TURN_SCALE = 0.7

# Set these to the axis indices for your controller
FORWARD_AXIS = 1   # left stick Y
TURN_AXIS    = 0   # left stick X
prev_message = '0'
pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()
print(f"Connected: {js.get_name()}\n")
prev_L= {"direction": 0 , "speed": 0}
prev_R = {"direction": 0, "speed": 0}
while True:
    if pygame.joystick.get_count() == 0:
        pygame.joystick.Joystick(0)
    pygame.event.pump()

    fwd  = -js.get_axis(FORWARD_AXIS)  # invert so forward = positive
    turn =  js.get_axis(TURN_AXIS)

    fwd  = fwd  if abs(fwd)  > DEADZONE else 0.0
    turn = turn if abs(turn) > DEADZONE else 0.0

    left  = max(-1.0, min(1.0, fwd + turn * TURN_SCALE))
    right = max(-1.0, min(1.0, fwd - turn * TURN_SCALE))

    L = {"direction": 0 if left  >= 0 else 1, "speed": int(abs(left)  * 255)}
    R = {"direction": 0 if right >= 0 else 1, "speed": int(abs(right) * 255)}

    message = str(R['direction']) + str(L['direction']) + str(R['speed']) + str(L['speed'])
    if int(message) == 0  :
        message = '00000000'


    if prev_L['direction'] != L['direction'] or prev_R['direction'] != R['direction'] or abs((prev_L['speed'] - L['speed'])/(1+L['speed'])) > 0.1 or abs((prev_R['speed'] - R['speed'])/(1+R['speed'])) > 0.1 or (int(message) == 0 and int(prev_message)!=0):
        client.publish("movement_controls",message)
        prev_L = L
        prev_R = R
        prev_message = message




    print(f"{message} hello {prev_L} hello {prev_message} hello {L}", end="\r")

