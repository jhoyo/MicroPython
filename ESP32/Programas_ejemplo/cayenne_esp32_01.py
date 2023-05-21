



# librerias

try:
  import usocket as socket
except:
  import socket

import network

from sys import exit

import esp
esp.osdebug(None)

import gc
gc.collect()

import sys
from random import randint

from machine import Pin, I2C
import ntptime
from utime import sleep_ms, sleep, localtime

#libreria para enlace y transmision MQTT
from cayenne import CayenneMQTTClient as MQTTClient
from cayenne import CayenneMessage
import logging

# librerias de los sensores
from BME680 import *  # sensor de presion, humedad y temperatura
from LTR390 import LTR390 

# enlace a internet via WiFi
station = network.WLAN(network.STA_IF)
station.active(False)
station.active(True)

# buscar Puntos de Acceso disponibles
lista = station.scan()
sleep(2)
ssid = ''
password = ''
if len(lista) == 0:
  print('No hay redes disponibles')
  exit()

# buscar los Puntos de Acceso para los que se tienen credenciales
for i in range(len(lista)):
  if lista[i][0] == b'SSID':    # cambiar SSID por el nombre de la red a conectar
    ssid = 'SSID'
    password = 'pwd'            # cambiar clave acceso a SSID
    i = len(lista)-1
  if lista[i][0] == b'LAB_IoT': # Ruter de la clase
    ssid = 'LAB_IoT'
    password = '12345678'
    i = len(lista)-1
  
def do_connect(ssid,pwd):
  if ssid == '':
    print("No hay Puntos de Acceso disponibles")
    exit()
  print('Conectando al Punto de Acceso...'+ssid)
  station.connect(ssid, pwd)
  
  # esperar conecci鐠愮珱
  while station.isconnected() == False:
    pass
  print('Configuracion de la Red:', station.ifconfig())
  
do_connect(ssid,password)

# Cayenne MQTT
usr = 'Usuario'                                     # copiar usuario del portal de Cayenne
pwd = 'Clave'                                       # copiar clave del portal de Cayenne 
cl_id = 'ID'                                        # copiar ID de cliente del portal de Cayenne 
srv = 'mqtt.mydevices.com'                          # servidor MQTT de Cayenne 
TOPIC = 'v1/{}/things/{}/data/'.format(usr, cl_id)  # Topico a publicar (enlace a Cayenne)

def on_message(msg):
  cmdMessage= CayenneMessage(msg[0],msg[1])  # message[0]: topic, message[1]:payload
  """
  cmdMessage.chanel contiene el valor del canal, tipo entero
  cmdMessage.value  continne el mensaje, tipo cadena
  """
  if cmdMessage.channel == 1:         # mensaje del canal 1, lampara
    lampara(cmdMessage.value)
  if cmdMessage.channel == 2:         # mensaje del canal 1, compresor de A/C
    compresor(cmdMessage.value)
  if cmdMessage.channel == 3:         # mensaje del canal 3, alarma de iluminacion
    alarma(cmdMessage.value)          

# configurar enlace a Cayenne
c = MQTTClient()
c.on_message = on_message
c.begin(usr,pwd,cl_id,loglevel=logging.INFO)

"""Variables usadas por Cayenne
# Data types
TYPE_BAROMETRIC_PRESSURE  = "bp"              # Barometric pressure
TYPE_BATTERY              = "batt"            # Battery
TYPE_LUMINOSITY           = "lum"             # Luminosity
TYPE_PROXIMITY            = "prox"            # Proximity
TYPE_RELATIVE_HUMIDITY    = "rel_hum"         # Relative Humidity
TYPE_TEMPERATURE          = "temp"            # Temperature
TYPE_VOLTAGE              = "voltage"         # Voltage
TYPE_DIGITAL_SENSOR       = "digital_sensor"  # digital sensor

# Unit types
UNIT_UNDEFINED            = "null"
UNIT_PASCAL               = "pa"              # Pascal
UNIT_HECTOPASCAL          = "hpa"             # Hectopascal
UNIT_PERCENT              = "p"               # % (0 to 100)
UNIT_RATIO                = "r"               # Ratio
UNIT_VOLTS                = "v"               # Volts
UNIT_LUX                  = "lux"             # Lux
UNIT_CENTIMETER           = "cm"              # Centimeter
UNIT_METER                = "m"               # Meter
UNIT_DIGITAL              = "d"               # Digital (0/1)
UNIT_FAHRENHEIT           = "f"               # Fahrenheit
UNIT_CELSIUS              = "c"               # Celsius
UNIT_KELVIN               = "k"               # Kelvin

UNIT_MILLIVOLTS           = "mv"              # Millivolts
"""
""" funciones para mandar datos a Cayenne
  
  celsiusWrite(channel,value)     : sends a temperature value in 鎺矯elsius
  fahrenheitWrite(channel,value)  : sends a temperature value in Fahrenheit
  kelvinWrite(channel,value)      : sends a temperature value in Kelvin
  humidityWrite(channel,value)    : send a relative humidity value in percent
  luxWite(channel,value)          : sends a light intensity value in lux
  pascalWrite(channel,value)      : sends a barometric pressure value in Pascal
  hectoPascalWrite(channel,value) : sends a barometric pressure value in hecto Pascal
  volatageWrite(channel,value)    : sends a voltage value in mV
  digitalWrite(channel,value)     : sends a digital value (0/1)
  """

"""
Inicializacion del canal I2C
"""
sda = Pin(21)                 # terminal SDA
scl = Pin(22)                 # terminal SCL
i2c = I2C(0,scl=scl,sda=sda)  # inicializacion interfaz I2C

bme = BME680_I2C(i2c=i2c, address=0x76) # iniciacion del sensor BME680 
s390 = LTR390(i2c, 0x53)                # iniciacion del sensor LTR390
"""
Inicializacion de los indicadores LED
"""
L1 = Pin(16, Pin.OUT)       # Lampara
L1.value(1)
L2 = Pin(17, Pin.OUT)       # salida a compresor
L2.value(1)
L3 = Pin(5, Pin.OUT)        # alarma de baja iluminacion
L3.value(1)

def lampara(valor):
  if valor == '1':
    L1.value(0)   # encender LED
  else:
    L1.value(1)   # apagar LED

def compresor(valor):
  if valor == '1':
    L2.value(0)   # encender LED
    c.digitalWrite(2, 1)
  else:
    L2.value(1)   # apagar LED
    c.digitalWrite(2, 0)
  sleep(2)
    
def alarma(valor,limite):
  if valor < limite:
    L3.value(0)   # encender LED
    c.digitalWrite(3, 1)
  else:
    L3.value(1)   # apagar LED
    c.digitalWrite(3, 0)
  sleep(2)
    
def main():
  try:
    while True:
      c.loop()
      t1 = bme.temperature
      p1 = bme.pressure
      h1 = bme.humidity
      l1 = s390.ALS()
      
      alarma(l1,300)              # revisar si la iluminacion est谩 por debajo de 300lx
      
      print('Temperatura ',t1)
      print('Presion ', p1)
      print('Humedad ', h1)
      print('Iluminacion ',l1)
      print('--------')
      
      c.celsiusWrite(11,t1)       # enviar temperatura a Cayenne
      c.hectoPascalWrite(12, p1)  # enviar presion en hectopascales a Cayebbe
      c.humidityWrite(13, h1)     # enviar humedad relativa a Cayenne 
      c.luxWrite(21, l1)          # enviar iluminacion a Cayenne
      
      sleep(5)
      
  except KeyboardInterrupt:
    print('Desconectando de '+ssid)
    station.disconnect()
    print('Cerrando programa')
    L1.value(1)
    L2.value(1)
    L3.value(1)
    exit()
  
  
if __name__ == '__main__':
  main()






