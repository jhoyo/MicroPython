# enlazar dos ESP32 usando ESPNow
import network
from machine import Pin
import espnow
import utime
from time import sleep, sleep_ms

# activar interfaz WLAN para ESPNow
sta = network.WLAN(network.STA_IF)  
sta.active(True)

# Inicializar ESPNow
esp = espnow.ESPNow()
esp.active(True)

# Definir la direccion MAC del ESP32 receptor (ESP32 B)
peer = b'\xE0\x5A\x1B\xA1\x0D\xC8'  # substituir con la dirección del ESP32
if esp.peer_count()[0] == 0:        # agregar peer solo si no existen antes
    esp.add_peer(peer)

# Crear el boton para enviar datos al presionarlo
boton = Pin(36, Pin.IN)

# Incializar variables para filtro de rebote
debounce_delay = 100     # Ajustar este valor de ser necesaior (milisegundos)
togle = 0               # memoria de estado encendido/apagado

while True:
    t = boton.value()   # ver estado del boton
    # Revisar si el estado del boton ha cambiado
    if t != 0:
        # Esperar a que el rebote del boton desaparesca
        sleep_ms(debounce_delay)
        
        # Volver a leer el estado del boton para asegurar estado estable
        t = boton.value()
        
        # si el estado del boton aun es 1, es una presion valida
        if t != 0:
            togle = not togle   # cambiar el estado anterior del interruptor
            if togle:
                message = "LedON"
            else:
                message = "LedOFF"
            print(f"Sending command : {message}")
            esp.send(peer, message)     # enviar mensaje al ESP32 B