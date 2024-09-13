# basado en el programa presentado en
#https://randomnerdtutorials.com/esp32-esp8266-micropython-web-server/
#
# Usar libreria de socket para poder crear un servidor WEB 
try:
    import usocket as socket 
except:   
    import socket  

# seccion de importacion de modulos 
from machine import Pin, ADC 
from time import sleep, sleep_ms
from onewire import OneWire
from ds18x20 import DS18X20  

import network          			# para conectar ESP32 a Wi-Fi  

import esp              			# apaga mensajes de debug del OS 
esp.osdebug(None)  

import gc               			# colector de basura 
gc.collect()  

ssid = 'Lab_IoT' 
password = '12345678'  

station = network.WLAN(network.STA_IF) 		# configurar ESP32 como estacion Wi-Fi  

station.active(True)                    	# activar estacion 
station.connect(ssid, password)         	# conectarse a Wi-Fi  

# esperar a conectarse a Wi-Fi 
while station.isconnected() == False:   
    pass  

print('Conexion exitosa') 
print(station.ifconfig()) 
print()  

led = Pin(2, Pin.OUT)

# configuración del interfaz 1-wire
ds = Pin(4)                             # conexion en GPIO 5
sensor = DS18X20(OneWire(ds))   		# definicion del sensor
ids = sensor.scan()             		# busca los DS18B20 conectados al interfaz  

# lo anterior podria estar en boot.py 

# función para leer valores del DS18B20  
def DS18():
  sensor.convert_temp()         		# solicita conversion de temperatura
  sleep_ms(750)                 		# tiempo maximo de conversion, 750ms
  temp2 = sensor.read_temp(ids[0]) 		# lectura del primer DS18B20 (unico)
  return temp2 

# funcion de pagina web 
def web_page():   
    if led.value() == 1:     
        gpio_state="ON"   
    else:     
        gpio_state="OFF"        
    temp2 = round(DS18(),2)      

    # texto en pagina web   
    html = """<html><head> <title>ESP32 Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css"
    integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr"
    crossorigin="anonymous">  
    <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}   
    h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; 
    background-color: #e7bd3b; border: none;    
    border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; 
    margin: 2px; cursor: pointer;}   
    .button2{background-color: #4286f4;}</style> 
    </head><body> <h1>ESP32 Web Server</h1>    
    <p>Estado de GPIO: <strong>""" + gpio_state + """   
    </strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>   
    <p><a href="/?led=off"><button class="button button2">OFF</button></a></p>   
    <p><i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
    <span class="ds-labels">Temperatura DS18B20:</span>
    <strong><span id="temperature">""" + str(temp2) + """</span></strong>
    <span class="units">&deg;C</span>
    </p>   
    </strong>   </body></html>"""   
    return html 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind(('', 80)) 
s.listen(5)  

while True:   
    try:     
        if gc.mem_free() < 102000:       
            gc.collect()     
        conn, addr = s.accept()     
        print('Se tiene coneccion de %s' % str(addr))     
        request = conn.recv(1024)     
        request = str(request)     
        print('Contenido = %s' % request)     
        led_on = request.find('/?led=on')     
        led_off = request.find('/?led=off')     
        if led_on == 6:       
            print('LED ON')       
            led.value(1)     
        if led_off == 6:       
            print('LED OFF')       
            led.value(0)     
        response = web_page()     
        conn.send('HTTP/1.1 200 OK\n')     
        conn.send('Content-Type: text/html\n')     
        conn.send('Connection: close\n\n')     
        conn.sendall(response)     
        conn.close()   
    except OSError as e:     
        conn.close()     
        print('Conexion Cerrada')
