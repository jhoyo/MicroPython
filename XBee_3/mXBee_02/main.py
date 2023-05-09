#
from machine import Pin, ADC, I2C
from time import sleep, sleep_ms

class BH1750():
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
        return (data[0]<<8 | data[1]) / (1.2 * factor)

# definicion de terminales
L1 = Pin("D0", Pin.OUT, value=1)    # led menos significativo
L2 = Pin("D2", Pin.OUT, value=1)    # led mas significativo
A3 = ADC("D3")                      # entrada analogica, sensor MCP9701


i2c = I2C(1)                        # inicializacion del canal I2C
sensor = BH1750(i2c)                # inicializacion del sensor BH1750

# funcion para leer y convertir la senal del convertirdor MCP9701
def t_an(adc):
    return ((adc.read() * 1.25 / 4095) - 0.4) / 0.0195  # en micropython la resolucion del XBEE es de 12 bits

def main():
    try:
        while True:
            print("Leds 00")
            L1.value(1)
            L2.value(1)
            print(t_an(A3), 'grados C')
            x = sensor.luminance(BH1750.ONCE_HIRES_1)
            print(x, ' lx\n')
            sleep(2)

            print("Leds 01")
            L1.value(0)
            L2.value(1)
            print(t_an(A3), 'grados C')
            x = sensor.luminance(BH1750.ONCE_HIRES_1)
            print(x, ' lx\n')
            sleep(2)

            print("Leds 10")
            L1.value(1)
            L2.value(0)
            print(t_an(A3), 'grados C')
            x = sensor.luminance(BH1750.ONCE_HIRES_1)
            print(x, ' lx\n')
            sleep(2)

            print("Leds 11")
            L1.value(0)
            L2.value(0)
            print(t_an(A3), 'grados C')
            x = sensor.luminance(BH1750.ONCE_HIRES_1)
            print(x, ' lx\n')
            sleep(2)

    except KeyboardInterrupt:
        print('Apagando LEDS')
        L1.value(1)
        L2.value(1)

if __name__ == "__main__":
    main()