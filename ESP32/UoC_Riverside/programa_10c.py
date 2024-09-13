
import network
import espnow
from machine import Pin

# Activar interfaz WLAN
sta = network.WLAN(network.STA_IF)
sta.active(True)

# Iniciar ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

led_pin = Pin(15, Pin.OUT)
led_pin.on()

while True:
    _, msg = esp.recv()
    if msg:             # msg == None if timeout in recv()
        if msg == b'LedON':
            print("Encender LED")
            led_pin.off()
        elif msg == b'LedOFF':
            print("Apagar LED")
            led_pin.on()
        else:
            print("Mensaje desconocido!")

