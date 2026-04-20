import random
from machine import Pin
from network import WLAN, STA_IF
from time import ticks_ms, ticks_diff, sleep
from thingsboard_sdk.tb_device_mqtt import TBDeviceMqttClient

# 1. Configuración del hardware
led = Pin(2, Pin.OUT)

# 2. Conexión WiFi (Tu configuración confirmada)
wlan = WLAN(STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Connecting to network...')
    wlan.connect("JAHM", "Bartolo123")
    while not wlan.isconnected():
        pass
print('Connected! Network config:', wlan.ifconfig())

# 3. Configuración de RPC (Control del LED desde la web)
def on_server_side_rpc_request(request_id, request_body):
    print("Comando recibido:", request_body)
    method = request_body.get('method')
    params = request_body.get('params')

    if method == "setLEDValue":
        led.value(1 if params else 0)
        print("LED físico:", "ENCENDIDO" if params else "APAGADO")
        val = True if led.value() else False
        msg = {"LEDvalue": val}
        client.send_telemetry(msg)
        print(msg)
        #client.send_attributes(msg)

# 4. Conexión a ThingsBoard
print("Conectando a thingsboard...")
client = TBDeviceMqttClient(host="thingsboard.cloud", port=1883, access_token="d8n00gh2iyljlnau2leq")
# Registramos la función que escuchará el botón del dashboard
client.set_server_side_rpc_request_handler(on_server_side_rpc_request)
client.connect()
print("Conectado a Thingsboard")
client.disconnect()