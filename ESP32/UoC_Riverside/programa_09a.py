# programas para uso del display SSD1306
from machine import Pin, SoftI2C
from time import sleep
import ssd1306 

i2c = SoftI2C(scl = Pin(22), sda = Pin(21))
print(i2c.scan())

oled_W = 128    # ancho de la pantalla en puntos
oled_H = 64     # alto de la pantalla en puntos
oled = ssd1306.SSD1306_I2C(oled_W, oled_H, i2c)

def main():
    oled.text('Hi UoC_Riverside', 0, 0)
    oled.text('Hola ITH', 0, 20)
    oled.text('Hola HMO', 0, 40)
    
    oled.show()
    
    sleep(2)
    
    oled.fill(1)
    oled.show()
    sleep(2)
    
    oled.poweroff()

if __name__ == "__main__":
    main()
