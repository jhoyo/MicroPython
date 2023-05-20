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

import ntptime
from utime import sleep_ms, sleep, localtime

#libreria para enlace y transmision MQTT
from cayenne import CayenneMQTTClient 
from cayenne import CayenneMessage
import logging

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
  if lista[i][0] == b'SSID':    # cambiar SSID por el nombre de la red a la que se va a conectar
    ssid = 'SSID'
    password = 'psw'            # clave de acceso del SSID a conectar
    i = len(lista)-1
  if lista[i][0] == b'LAB_IoT': # SSID del ruter del laboratorio
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
usr = 'usuario cayennene'         # copiar usuario del portal de Cayenne
pwd = 'clave cayene'              # copiar clave del portal de Cayenne 
cl_id = 'ID cliente cayenne'      # copiar ID de cliente del portal de Cayenne 
srv = 'mqtt.mydevices.com'                          # servidor MQTT de Cayenne 
TOPIC = 'v1/{}/things/{}/data/'.format(usr, cl_id)  # Topico a publicar (enlace a Cayenne)

def on_message(msg):
  #print(msg)
  #print('Mensaje Recibido: ' + str(msg))
  cmdMessage= CayenneMessage(msg[0],msg[1])  # message[0]: topic, message[1]:payload
  print("Channel: %d"%cmdMessage.channel)
  print("value: %s"%cmdMessage.value)
  
# configurar enlace a Cayenne
c = CayenneMQTTClient()
c.on_message = on_message
c.begin(usr,pwd,cl_id,loglevel=logging.INFO)

 
def main():
  try:
    while True:
      sleep(2)
      
  except KeyboardInterrupt:
    print('Desconectando de '+ssid)
    station.disconnect()
    print('Cerrando programa')
    exit()
  
  
if __name__ == '__main__':
  main()
