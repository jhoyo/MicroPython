# SPDX-License-Identifier: Apache-2.0

import gc, sys, time, machine, json, asyncio
import config
from umqtt.simple import MQTTClient, MQTTException

# ---------------- Callbacks ----------------
def _dummy(*args):
    pass

on_connected = _dummy
on_disconnected = _dummy
on_message = _dummy

firmware_version = "0.0.1"

# ---------------- MQTT message handler ----------------
def _on_message(topic, payload):
    topic = topic.decode()
    payload = payload.decode()

    if topic == "downlink/reboot":
        machine.reset()
    elif topic == "downlink/ping":
        pass
    else:
        on_message(topic, payload)

# ---------------- TLS ----------------
ssl_ctx = None
if sys.platform in ("esp32", "rp2"):
    import ssl
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.load_verify_locations(cafile="ISRG_Root_X1.der")

# ---------------- MQTT client ----------------
mqtt = MQTTClient(
    client_id="",
    server=config.BLYNK_MQTT_BROKER,
    user="device",
    password=config.BLYNK_AUTH_TOKEN,
    ssl=ssl_ctx,
    keepalive=45
)
mqtt.set_callback(_on_message)

# ---------------- Connect ----------------
async def _mqtt_connect():
    gc.collect()
    mqtt.connect()
    mqtt.subscribe("downlink/#")

    info = {
        "type": config.BLYNK_TEMPLATE_ID,
        "tmpl": config.BLYNK_TEMPLATE_ID,
        "ver": firmware_version,
        "rxbuff": 1024
    }
    mqtt.publish("info/mcu", json.dumps(info))
    on_connected()

# ---------------- Main task ----------------
async def task():
    connected = False

    while True:
        await asyncio.sleep_ms(20)

        if not connected:
            try:
                await _mqtt_connect()
                connected = True
            except Exception as e:
                print("MQTT connect error:", e)
                await asyncio.sleep(5)

        else:
            try:
                mqtt.check_msg()
            except OSError as e:
                # errno 11 = no data (normal)
                if e.args and e.args[0] == 11:
                    pass
                else:
                    connected = False
                    on_disconnected()
            except Exception:
                connected = False
                on_disconnected()