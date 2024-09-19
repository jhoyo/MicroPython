# librerias generales
from network import WLAN, STA_IF
from time import sleep, sleep_ms, time
from machine import Pin, I2C
from sys import exit
import esp
import gc
from umqtt.robust import MQTTClient

from bmp280 import BMP280
from bh1750 import BH1750
from ahtx0 import AHT20
from math import log
from onewire import OneWire
from ds18x20 import DS18X20

esp.osdebug(None)
gc.collect()

# Pines de salida
luz1 = Pin(14, Pin.OUT) # Interruptor de Luz
comp = Pin(13, Pin.OUT) # Compresor A/C
alar = Pin(12, Pin.OUT)  # Alarma iluminacion
# todas las salidas apagadas
luz1.on()
comp.on()
alar.on()

i2c = I2C(0,scl=Pin(22), sda=Pin(21))
bmp = BMP28(i2c)
ltr = BH1750(i2c)
ds1 = DS18X20(OneWire(Pin(4)))
rds = ds1.scan()
ath = ATH20(i2c)

station = WLAN(STA_IF)
station.active(False)
station.active(True)

# buscar Puntos de Acceso disponibles
lista = station.scan()
ssid = ''
password = ''

# buscar los Puntos de Acceso para los que se tienen credenciales
for i in range(len(lista)):
  if lista[i][0] == b'LAB_IoT':
    ssid = '12345678'
    password = ''
    i = len(lista)-1
  if lista[i][0] == b'reemplazar con su SSID':
    ssid = 'reemplazar con su SSID'
    password = 'reemplazar con su password'
    i = len(lista)-1

# funciones para conexion Wi-Fi
def conectar(ssid,pwd):
  if ssid == '':
    print("No hay Puntos de Acceso disponibles")
    exit()
  
  # esperar coneccion
  while station.isconnected() == False:
    print('Conectando al Punto de Acceso...'+ssid)
    station.connect(ssid, pwd)
    sleep(1)
  print('Configuracion de la Red:', station.ifconfig())
    
def revisarwifi():
    while not station.isconnected():
        sleep_ms(500)
        print(".")
        station.connect()
    
print("Inicio\n")
conectar(ssid,password)
sleep(2)
        
# funciones enlace MQTT a UBIDOTS
def publicar(topic, payload):    #mandar mensaje al servidor MQTT de UBIDOTS
    try:
        client.publish(topic, payload)
    except Exception as e:
        print("Dato no subido, razon - ",e)
    else:
        print("Dato publicado")
    sleep_ms(500)
    
def recibir(topic,payload):
    print('-----------')
    print("topic =", topic)
    print("valor =", payload)
    print('-----------\n')
    if topic == b"/v1.6/devices/esp32/luz_of_1/lv": # Interruptor de la Luz
        if payload == b'1.0':   # si el botón está en ON
            luz1.off()          # prender el LED luz
        else:                   # si el botón está en OFF
            luz1.on()           # apagar el LED luz

    if topic == b"/v1.6/devices/esp32/compresor_of_1/lv": # compresor A/C
        if payload == b'1.0':   # si el botón está en ON
            comp.off()          # prender el LED luz
        else:                   # si el botón está en OFF
            comp.on()           # apagar el LED luz

    if topic == b"/v1.6/devices/esp32/alarma_of_1/lv": # alarma iluminacion
        if payload == b'1.0':   # si el botón está en ON
            alar.off()          # prender el LED alarma
        else:                   # si el botón está en OFF
            alar.on()           # apagar el LED alarma
            
# funciones para enviar señales sensadas a UBIDOTS 
def env_temp1(var1):
    payload = b'{"temp_of_1": %d}' % (var1)
    print(payload)
    publicar(topic,payload)
    
def env_hum(var1):
    payload = b'{"hr_of_1": %d}' % (var1)
    print(payload)
    publicar(topic,payload)

def env_pres(var1):
    payload = b'{"presion_of_1": %d}' % (var1)
    print(payload)
    publicar(topic,payload)
    
def env_ilum(var1):
    payload = b'{"ilum_of_1": %d}' % (var1)
    print(payload)
    publicar(topic,payload)
    
def env_temp2(var1):
    payload = b'{"temp_pasillo_of_1": %d}' % (var1)
    print(payload)
    publicar(topic,payload)
       
# Configuración Ubidots
Token    = "reemplazar con su token"
clientID = "reemplazar con su ID"
URL      = "industrial.api.ubidots.com"
topic    = b'/v1.6/devices/ESP32'

client = MQTTClient(clientID, URL, 1883, user = Token, password = Token) 
client.set_callback(recibir)                        # definir la función que recibirá los mensajes de UBIDOTS
client.connect()                                    # iniciar conexion
topic1 = b"/v1.6/devices/esp32/luz_of_1/lv"         # interruptor de luz
client.subscribe(topic1)
topic2 = b"/v1.6/devices/esp32/compresor_of_1/lv"   # Activador del compresor
client.subscribe(topic2)
topic3 = b"/v1.6/devices/esp32/alarma_of_1/lv"      # alarma de iluminacion
client.subscribe(topic3)

def main():
    revisarwifi()
    t0 = time()
    t1 = time()
    tf1 = 30
    tf2 = 15
    
    i = 0
    while True:
        try:
            client.check_msg()
            if (time() - t0) >= tf1: # enviar temperatura y humedad cada 30 segundos
                env_temp1(round(thr.temperature, 2))
                env_hum(round(thr.relative_humidity, 2)) 
                ds1.convert_temp()
                sleep_ms(750)
                temp2 = 1
                env_temp2(round(ds1.read_temp(rds[0]),2))                
                t0 = time()
            if (time() - t1) >= tf2: # enviar presion e iluminacion cada 15 segundos
                env_pres(round(bmp.pressure,2))
                env_ilum(round(ltr.luminance(BH1750.ONCE_HIRES_2),2))
                t1 = time()
            sleep(1)     

        except OSError as e:
            print(e)
            print('final')
            client.disconnect()
            station.connect(False)
            exit()
    
if __name__ == "__main__":
    main()
