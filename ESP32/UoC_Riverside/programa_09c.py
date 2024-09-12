# programas para uso del display SSD1306
from machine import Pin, SoftI2C
from time import sleep
import ssd1306 as ssd1306 
from onewire import OneWire # importar funciones para protocolo 1-wire 
from ds18x20 import DS18X20 # importar funcion para sensor DS18B20
import framebuf

i2c = SoftI2C(scl = Pin(22), sda = Pin(21))

oled_W = 128    # ancho de la pantalla en puntos
oled_H = 64     # alto de la pantalla en puntos
oled = ssd1306.SSD1306_I2C(oled_W, oled_H, i2c)

DS = Pin(4)                 # conexion al DS18B20
sensor = DS18X20(OneWire(DS))

t = [0x00, 0x00, 0x00, 0x00, 0x07, 0xC0, 0x00, 0x00, 0x07, 0xE0, 0x00, 0x18, 0x04, 0x20, 0x00, 0x18,
     0x04, 0x38, 0x00, 0x3C, 0x04, 0x20, 0x00, 0x24, 0x04, 0x30, 0x00, 0x66, 0x04, 0x30, 0x00, 0x24,
     0x04, 0x20, 0x00, 0x3C, 0x05, 0xB8, 0x00, 0x00, 0x05, 0xA0, 0x06, 0x00, 0x05, 0xA0, 0x0E, 0x00,
     0x05, 0xB0, 0x0B, 0x00, 0x05, 0xA0, 0x19, 0x00, 0x05, 0xB8, 0x11, 0x80, 0x05, 0xA0, 0x11, 0x80,
     0x05, 0xA0, 0x1B, 0x00, 0x0D, 0xA0, 0x0E, 0x00, 0x19, 0xB8, 0x00, 0x18, 0x31, 0x8C, 0x00, 0x18,
     0x21, 0x84, 0x00, 0x24, 0x67, 0xC6, 0x00, 0x66, 0x47, 0xE2, 0x00, 0x42, 0x47, 0xE2, 0x00, 0x42,
     0x47, 0xE2, 0x00, 0x42, 0x47, 0xC6, 0x00, 0x7E, 0x61, 0x84, 0x00, 0x18, 0x30, 0x0C, 0x00, 0x00,
     0x18, 0x18, 0x00, 0x00, 0x0F, 0xF0, 0x00, 0x00, 0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
term = bytearray(t)

def centigrados(rom):
    sensor.convert_temp()   # iniciar el convertidor de temperatura DS18B20
    sleep(0.75)             # esperar a completar la conversion
    return sensor.read_temp(rom)
 
def farenheit(rom):
    t = centigrados(rom)
    return (t*9/5)+32

def main():
    roms = sensor.scan()     # buscar direccion del sensor DS18B20
    if len(roms) == 0:
        print("NO hay ningun DS18B20 conectado al ESP32")
        exit(0)
    rom = roms[0]
    
    while True:
        fb = framebuf.FrameBuffer(term, 32, 32, framebuf.MONO_HLSB)
        oled.blit(fb,0,20)
        oled.fill_rect(60,18, 45,30,0)
        
        t = centigrados(rom)
        f = farenheit(rom)
        
        # Desplegar valor de temperatura con dos decimales.
        oled.text(str('T: ' +"{:0.2f}".format(t)+ "  C",2),40,19)

        # Desplegar valor de temperatura con dos decimales.
        oled.text(str('T: ' +"{:0.2f}".format(f)+ "  F",2),40,39)
        
        # dibujar simbolo de grado, un cuadrado de 4x4.
        oled.fill_rect(113, 18, 4,4, 1)
        oled.fill_rect(113, 38, 4,4, 1)
        
        oled.show()
        sleep(2)
        #oled.fill_rect(60,18, 45,30,0)
        #oled.show()
    oled.poweroff()

if __name__ == "__main__":
    main()
