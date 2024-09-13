# programa para obtener la direccion MAC de un ESP32
import network

# inicializar el interfaz de red
wlan = network.WLAN(network.STA_IF)

# activar el interfaz WLAN
wlan.active(True)

# revisar si el interfaz esta activo (conectado)
if wlan.active():
    # obtener la direccion MAC
    mac_address = wlan.config("mac")
    print(mac_address)
    print("La direccion MAC del ESP32:", ":".join(["{:02X}".format(byte) for byte in mac_address]))
else:
    print("Wi-Fi NO esta activo.")