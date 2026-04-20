from network import WLAN, STA_IF
from time import sleep, ticks_ms, ticks_diff
from random import getrandbits
from machine import Pin
from thingsboard_sdk.tb_device_mqtt import TBDeviceMqttClient

# 1. Configuración del hardware
led = Pin(2, Pin.OUT)

# 2. Conexión WiFi (Tu configuración confirmada)
wlan = WLAN(STA_IF)
wlan.active(True)
SSID = "CasaHM"
PASS = "PepeyLety1995"
if not wlan.isconnected():
    print('Conectando a la red...')
    wlan.connect(SSID, PASS)
    while not wlan.isconnected():
        pass
print('Conectada! Configuracion de la red:', wlan.ifconfig())

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

# 5. Bucle de envío de datos
ultimo_envio = 0
intervalo_telemetria = 5000 # 5 segundos en milisegundos

try:
    while True:
        # 1. REVISAR MENSAJES CONSTANTEMENTE (Respuesta rápida al Switch)
        try:
            client.check_for_msg()
        except:
            pass
            
        # 2. ENVIAR TELEMETRÍA SOLO CADA 5 SEGUNDOS
        millis_actuales = ticks_ms()
        if ticks_diff(millis_actuales, ultimo_envio) >= intervalo_telemetria:
            temp_simulada = 22.0 + (getrandbits(10) / 1024) * 5
            telemetria = {"temperature": round(temp_simulada, 2)}
            client.send_telemetry(telemetria)
            print(f"Telemetría enviada: {temp_simulada:.2f}°C")
            ultimo_envio = millis_actuales
            
        # Pausa mínima para no saturar el procesador, pero suficiente para ser veloz
        sleep(0.2) 

except Exception as e:
    print("Error en el bucle:", e)
    client.disconnect()