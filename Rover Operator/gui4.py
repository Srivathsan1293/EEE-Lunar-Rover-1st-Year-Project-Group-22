import asyncio
import json
import paho.mqtt.client as mqtt
import websockets
import pygame

# ── Joystick setup ────────────────────────────────────────────────────────────
pygame.init()
pygame.joystick.init()
js = None
if pygame.joystick.get_count() > 0:
    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"[Joystick] connected: {js.get_name()}")
else:
    print("[Joystick] no controller found")
# ─────────────────────────────────────────────────────────────────────────────

connected_browsers = set()
latest_sensors = {"s1": 0.0, "s2": 0.0, "s3": 0.0, "s4": 0.0}
pending_broadcast = asyncio.Event()
loop = None

def on_mqtt_message(client, userdata, msg):
    global latest_sensors
    try:
        data = json.loads(msg.payload.decode())
        latest_sensors.update(data)
        if loop:
            loop.call_soon_threadsafe(pending_broadcast.set)
    except Exception as e:
        print(f"[MQTT] error: {e}")

async def broadcast(message):
    dead = set()
    for ws in connected_browsers:
        try:
            await ws.send(message)
        except Exception:
            dead.add(ws)
    connected_browsers.difference_update(dead)

async def ws_handler(websocket):
    print(f"[WS] browser connected: {websocket.remote_address}")
    connected_browsers.add(websocket)
    try:
        await websocket.send(json.dumps(latest_sensors))
        async for message in websocket:
            print(f"[WS] command from browser: {message}")
            mqtt_client.publish("rover/cmd", message)
    except Exception as e:
        print(f"[WS] connection error: {e}")
    finally:
        connected_browsers.discard(websocket)
        print(f"[WS] browser disconnected")

async def joystick_loop():
    while True:
        pygame.event.pump()

        if pending_broadcast.is_set():
            button_held = js and js.get_button(0)

            # always send sensor data so cards update live
            payload = dict(latest_sensors)

            # only include log flag if button A is pressed
            if button_held:
                payload["log"] = True

            await broadcast(json.dumps(payload))
            pending_broadcast.clear()

        await asyncio.sleep(1 / 50)

async def main():
    global loop
    loop = asyncio.get_running_loop()
    mqtt_client.loop_start()

    url = "http://localhost:8765"
    hyperlink = f"\033]8;;{url}\033\\{url}\033]8;;\033\\"
    print(f"[Bridge] running on {hyperlink}")

    async with websockets.serve(ws_handler, "localhost", 8765):
        await joystick_loop()

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_mqtt_message
mqtt_client.connect("localhost", 1883)
mqtt_client.subscribe("rover/sensors")

asyncio.run(main())