import urequests
import mip

from time import time, sleep
from network import WLAN, STA_IF


# Conectar ESP32 a Wi-Fi
def conectar_wifi(ssid, password, timeout=10):
    wlan = WLAN(STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Conectando a {ssid}...")
        wlan.connect(ssid, password)
        
        # Bucle de espera con timeout para evitar bloqueos infinitos
        start_time = time()
        while not wlan.isconnected():
            if time() - start_time > timeout:
                print("\nError: Tiempo de espera agotado.")
                return False
            print(".", end="")
            sleep(1)
            
    print("\nConexión exitosa!")
    print("Configuración de red:", wlan.ifconfig())
    return True

# claves de acceso a Wi-Fi
SSID = "tecnm_hillo"
PASS = ""
conectar_wifi(SSID, PASS)


# Instalar libreria MQTT de Thingsboard
print("Instalar libreria thingsboard-micropython-cliend-sdk")

mip.install('github:thingsboard/thingsboard-micropython-client-sdk')


