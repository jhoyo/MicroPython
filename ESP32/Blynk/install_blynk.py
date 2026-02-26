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
SSID = "nombre del SSID"
PASS = "contraseña del SSID"
conectar_wifi(SSID, PASS)

# Instalar libreria MQTT de Blynk
print("Instalar libreria blynk_mqtt.py")
base = "github:jhoyo/Micropython/ESP32/Blynk/"
mip.install("github:jhoyo/Micropython/ESP32/Blynk/lib/blynk_mqtt.py")

# instalar archivos boot.py, demo.py y conf.py en raiz
print("Instalar archivo boot.py")
mip.install(base+"boot.py",target = "/")
print("Instalar archivo config.py")
mip.install(base+"config.py",target = "/")
print("Instalar archivo demo.py")
mip.install(base+"demo.py",target = "/")

# Instalar el archivo binario de acceso SSL
# 1. Definir la URL Raw (directa) del certificado
url = "https://raw.githubusercontent.com/jhoyo/MicroPython/main/ESP32/Blynk/ISRG_Root_X1.der"

# 2. Hacer la petición
print("Descargando...")
res = urequests.get(url)

if res.status_code == 200:
    # 3. Escribir el archivo en la raíz en modo binario (wb)
    with open("ISRG_Root_X1.der", "wb") as f:
        f.write(res.content)
    print("¡Archivo grabado en la raíz exitosamente!")
else:
    print("Error al descargar. Código:", res.status_code)

res.close()
