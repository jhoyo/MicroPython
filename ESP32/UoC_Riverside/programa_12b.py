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

station = network.WLAN(network.STA_IF)
station.active(True)

# buscar Puntos de Acceso disponibles
lista = station.scan()
ssid = ''
password = ''

# buscar los Puntos de Acceso para los que se tienen credenciales
for i in range(len(lista)):
  if lista[i][0] == b'tecnm_hillo':
    ssid = 'tecnm_hillo'
    password = ''
    i = len(lista)-1
  if lista[i][0] == b'Lab_IoT':
    ssid = 'Lab_IoT'
    password = '12345678'
    i = len(lista)-1
  
def do_connect(ssid,pwd):
  if ssid == '':
    print("No hay Puntos de Acceso disponibles")
    exit()
  print('Conectando al Punto de Acceso...'+ssid)
  station.connect(ssid, pwd)
  
  # esperar coneccion
  while station.isconnected() == False:
    pass
  print('Configuracion de la Red:', station.ifconfig())
  #station.disconnect()
 
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
 
do_connect(ssid,password)
