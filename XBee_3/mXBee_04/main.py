# Default template for Digi projects
from machine import Pin, ADC, I2C
from time import sleep, sleep_ms
from xbee import atcmd, transmit, ADDR_COORDINATOR  	# para comunicacion en red ZigBee
from BH1750 import *

# definicion de terminales
L1 = Pin("D0", Pin.OUT, value=1)    # led ON
L2 = Pin("D2", Pin.OUT, value=1)    # led Compresor
A3 = ADC("D3")                      # entrada analogica, sensor MCP9701
L4 = Pin("D4", Pin.OUT, value=0)    # indicador de solicitud de información remota
L6 = Pin('D6', Pin.OUT, value=1)    # led Ventana

i2c = I2C(1)                        # inicializacion del canal I2C
sensor = BH1750(i2c)                # inicializacion del sensor BH1750

lim_temp    = 26                    # limite de temperatura maxima para activar alarma
ventana     = 3                     # ventana de temperatura para termostato

# funcion para leer y convertir la senal del convertirdor MCP9701
def t_an(adc):
    return ((adc.read() * 1.25 / 4095) - 0.4) / 0.0195  # en micropython la resolucion del XBEE es de 12 bits

# funcion para mandar al coordinador las lecturas de los sensores
def remoto(temp, ilum):
    print('se activo el pin DIO4')
    cadena = temp + ',' + ilum
    try:
        transmit(ADDR_COORDINATOR, cadena)
    except Exception as err:
        print(err)
    L4.value(0)

def network_status():   	# ver si esta conectado a una red ZigBee
    return atcmd("AI")

def main():
    while network_status() != 0:		# esperar hasta estar conectado a una red ZigBee
        sleep_ms(100)
    print('Conectado a una RED ZigBee\n')

    # señalizacion de red conectada y modulo listo para tomar mediciones
    L1.value(0)     # encender L1
    sleep(5)
    L1.value(1)     # apagar L1
    L2.value(0)     # encender L2
    sleep(5)
    L2.value(1)     # apagar L2
    L6.value(0)     # encender L6
    sleep(5)
    L6.value(1)     # apagar L6
    print('Listo para transmitir')

    # lazo principal de lectura de sensores
    try:
        while True:
            temp1 = t_an(A3)
            if temp1 > lim_temp+ventana:
                L2.value(0)                             # activar compresor
            if temp1 < lim_temp-ventana:
                L2.value(1)                             # desactivar compresor
            temp = '{:.3f}'.format(temp1)             	# lectura de temperatura y conversion a cadena formato xxx.xxx
            print(temp, 'grados C')
            l1 = sensor.luminance(BH1750.ONCE_HIRES_1)
            if l1 < 300:
                L6.value(0)                             # activar persiana
            if l1 > 1000:
                L6.value(1)                             # desactivar persiana
            luz = '{:.3f}'.format(l1)           		# lectura de iluminacion y conversion a cadena formato xxx.xxx
            print(luz, 'lx\n')
            if L4.value() == 1:
                remoto(temp, luz)       		        # verificar si hay solicitud de informacion
            sleep(2)                                    # lazo de dos segundos entre mediciones

    except KeyboardInterrupt:
        print('Apagando LEDS')
        L1.value(1)
        L2.value(1)
        L6.value(1)

if __name__ == "__main__":
    main()