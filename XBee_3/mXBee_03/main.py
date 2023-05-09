# modulos a cargar
from machine import Pin, ADC, I2C                   # manejo de terminales del XBee
from time import sleep, sleep_ms                    # funciones de retardo
from xbee import atcmd, transmit, ADDR_COORDINATOR  # para comunicacion en red ZigBee


class BH1750:
    """Micropython BH1750 ambient light sensor driver."""
    PWR_OFF = 0x00
    PWR_ON  = 0x01
    RESET   = 0x07

    # modes
    CONT_LOWRES     = 0x13
    CONT_HIRES_1    = 0x10
    CONT_HIRES_2    = 0x11
    ONCE_HIRES_1    = 0x20
    ONCE_HIRES_2    = 0x21
    ONCE_LOWRES     = 0x23

    # default addr=0x23 if addr pin floating or pulled to ground
    # addr=0x5c if addr pin pulled high
    def __init__(self, bus, addr=0x23):
        self.bus = bus
        self.addr = addr
        self.off()
        self.reset()

    def off(self):
        """Turn sensor off."""
        self.set_mode(self.PWR_OFF)

    def on(self):
        """Turn sensor on."""
        self.set_mode(self.PWR_ON)

    def reset(self):
        """Reset sensor, turn on first if required."""
        self.on()
        self.set_mode(self.RESET)

    def set_mode(self, mode):
        """Set sensor mode."""
        self.mode = mode
        self.bus.writeto(self.addr, bytes([self.mode]))

    def luminance(self, mode):
        """Sample luminance (in lux), using specified sensor mode."""
        # continuous modes
        if mode & 0x10 and mode != self.mode:
            self.set_mode(mode)
        # one shot modes
        if mode & 0x20:
            self.set_mode(mode)
        # earlier measurements return previous reading
        sleep_ms(24 if mode in (0x13, 0x23) else 180)
        data = self.bus.readfrom(self.addr, 2)
        factor = 2.0 if mode in (0x11, 0x21) else 1.0
        return (data[0] << 8 | data[1]) / (1.2 * factor)


# definicion de terminales
L1 = Pin("D0", Pin.OUT, value=1)    # led limite temperatura
L2 = Pin("D2", Pin.OUT, value=1)    # led limite iluminacion
A3 = ADC("D3")                      # entrada analogica, sensor MCP9701
L4 = Pin("D4", Pin.OUT, value=0)    # indicador de solicitud de información remota

# apertura canal I2C
i2c = I2C(1)                        # inicializacion del canal I2C, SCL en DIO1 y SDA en DIO11
sensor = BH1750(i2c)                # inicializacion del sensor BH1750

lim_temp = 27                       # limite de temperatura maxima para activar alarma
lim_ilum = 300                      # limite de ilumininacion minima para activar alarma


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


def network_status():   # ver si esta conectado a una red ZigBee
    return atcmd("AI")


def main():
    while network_status() != 0:
        sleep_ms(100)
    print('Conectado a una RED ZigBee\n')

    # señalizacion de red conectada y modulo listo para tomar mediciones
    L1.value(0)     # encender L1
    sleep(1)
    L1.value(1)     # apagar L1
    L2.value(0)     # encender L2
    sleep(1)
    L2.value(1)     # apagar L2

    # lazo principal de lectura de sensores
    try:
        while True:
            t1 = t_an(A3)
            if t1 > lim_temp:
                L1.value(0)                             # activar alarma
            else:
                L1.value(1)                             # desactivar alarma
            temp = '{:.3f}'.format(t1)                  # lectura de temperatura y conversion a cadena formato xxx.xxx
            print(temp, 'grados C')
            l1 = sensor.luminance(BH1750.ONCE_HIRES_1)
            if l1 < lim_ilum:
                L2.value(0)                             # activar alarma
            else:
                L2.value(1)                             # desactivar alarma
            luz = '{:.3f}'.format(l1)                   # lectura de iluminacion y conversion a cadena formato xxx.xxx
            print(luz, 'lx\n')
            if L4.value() == 1:
                remoto(temp, luz)       # verificar si hay solicitud de informacion
            sleep(2)                                    # lazo de dos segundos entre mediciones

    except KeyboardInterrupt:
        print('Apagando LEDS')
        L1.value(1)
        L2.value(1)


if __name__ == "__main__":
    main()
