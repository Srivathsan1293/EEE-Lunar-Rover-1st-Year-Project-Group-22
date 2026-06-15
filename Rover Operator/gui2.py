import asyncio
import json
import paho.mqtt.client as mqtt
import websockets

connected_browsers = set()
latest_sensors = {"s1": 0.0, "s2": 0.0, "s3": 0.0, "s4": 0.0}
loop = None

def on_mqtt_message(client, userdata, msg):
    global latest_sensors
    try:
        data = json.loads(msg.payload.decode())
        latest_sensors.update(data)
        print(f"[MQTT] received: {data} | browsers connected: {len(connected_browsers)}")
        if loop and connected_browsers:
            future = asyncio.run_coroutine_threadsafe(
                broadcast(json.dumps(latest_sensors)), loop
            )
            future.result(timeout=2)
    except Exception as e:
        print(f"[MQTT] error: {e}")

async def broadcast(message):
    dead = set()
    for ws in connected_browsers:
        try:
            await ws.send(message)
        except Exception:
            dead.add(ws)      # remove broken connections
    connected_browsers.difference_update(dead)

async def ws_handler(websocket):
    print(f"[WS] browser connected: {websocket.remote_address}")
    connected_browsers.add(websocket)
    try:
        await websocket.send(json.dumps(latest_sensors))  # send immediately on connect
        async for message in websocket:
            print(f"[WS] command from browser: {message}")
            mqtt_client.publish("rover/cmd", message)
    except Exception as e:
        print(f"[WS] connection error: {e}")
    finally:
        connected_browsers.discard(websocket)
        print(f"[WS] browser disconnected")

async def main():
    global loop
    loop = asyncio.get_running_loop()
    mqtt_client.loop_start()

    async with websockets.serve(ws_handler, "localhost", 8765):
        print("[Bridge] running on ws://localhost:8765")
        await asyncio.Future()

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_mqtt_message
mqtt_client.connect("localhost", 1883)
mqtt_client.subscribe("rover/sensors")

asyncio.run(main())