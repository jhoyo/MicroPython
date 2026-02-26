# SPDX-FileCopyrightText: 2024 Volodymyr Shymanskyy for Blynk Technologies Inc.
# SPDX-License-Identifier: Apache-2.0

import sys, asyncio, ntptime
import time
from machine import Pin
import network
from math import sin

import config
import blynk_mqtt

BLYNK_FIRMWARE_VERSION = "0.1.0"

# ---------- Hardware ----------
led = Pin(2, Pin.OUT)
led.value(0)  # LED apagado (activo LOW)

# ---------- Estado ----------
connected_flag = False
last_state = None
t0 = time.time()


# ---------- WiFi ----------
def connect_wifi():
    sta = network.WLAN(network.STA_IF)
    if not sta.isconnected():
        print(f"Connecting to {config.WIFI_SSID}...", end="")
        sta.active(True)
        sta.disconnect()
        sta.config(reconnects=5)
        sta.connect(config.WIFI_SSID, config.WIFI_PASS)
        while not sta.isconnected():
            time.sleep(1)
            print(".", end="")
        print(" OK:", sta.ifconfig()[0])

connect_wifi()

def sync_time():
    try:
        ntptime.server = "pool.ntp.org"
        ntptime.timeout = 5
        ntptime.settime()
        print("Hora sincronizada:", time.gmtime())
    except Exception as e:
        print("NTP error:", e)

sync_time()

# ---------- Blynk callbacks ----------
async def delayed_sync():
    await asyncio.sleep_ms(500)
    print("Solicitando estado V0")
    blynk_mqtt.mqtt.publish("get/ds","Integer V0")
    
def mqtt_connected():
    global connected_flag #, last_state
    print("MQTT conectado")
    connected_flag = True

    asyncio.create_task(delayed_sync())

def mqtt_disconnected():
    global connected_flag
    print("MQTT desconectado")
    connected_flag = False

def mqtt_callback(topic, payload):
    print("RX:", topic, payload)

    if topic.startswith("downlink/ds/Integer V0"):
        if payload == "1":
            led.value(1)   # ON
        else:
            led.value(0)   # OFF

# ---------- Update task ----------
async def update_task():
    global last_state
    while True:
        try:
            if connected_flag:
                state = "1" if led.value() == 1 else "0"
                if state != last_state:
                    blynk_mqtt.mqtt.publish("ds/Integer V0", state)
                    last_state = state
                
                # ----- Temperatura simulada -----
                elapsed = time.time() - t0
                temp = 25 + 5 * sin(elapsed / 10)  # °C
                temp_str = "{:.2f}".format(temp)

                blynk_mqtt.mqtt.publish("ds/Double V1", temp_str)
                print("Temperatura enviada:", temp_str, "°C")
        except Exception as e:
            print("Update error:", e)

        await asyncio.sleep(2)

# ---------- Start ----------
blynk_mqtt.on_connected = mqtt_connected
blynk_mqtt.on_disconnected = mqtt_disconnected
blynk_mqtt.on_message = mqtt_callback
blynk_mqtt.firmware_version = BLYNK_FIRMWARE_VERSION

try:
    asyncio.run(asyncio.gather(
        blynk_mqtt.task(),
        update_task()
    ))
except KeyboardInterrupt:
    print("Interrupted")
finally:
    asyncio.new_event_loop()