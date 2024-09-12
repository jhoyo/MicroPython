# programas para uso del display SSD1306
from machine import Pin, SoftI2C
from time import sleep
import ssd1306 
import framebuf

i2c = SoftI2C(scl = Pin(22), sda = Pin(21))

oled_W = 128    # ancho de la pantalla en puntos
oled_H = 64     # alto de la pantalla en puntos
oled = ssd1306.SSD1306_I2C(oled_W, oled_H, i2c)

screen1_row1 = "Screen 1, row 1"
screen1_row2 = "Screen 1, row 2"
screen1_row3 = "Screen 1, row 3"

screen2_row1 = "Screen 2, row 1"
screen2_row2 = "Screen 2, row 2"

screen3_row1 = "Screen 3, row 1"

screen1 = [[0, 0 , screen1_row1], [0, 16, screen1_row2], [0, 32, screen1_row3]]
screen2 = [[0, 0 , screen2_row1], [0, 16, screen2_row2]]
screen3 = [[0, 40 , screen3_row1]]

# Scroll in screen horizontally from left to right
def scroll_in_screen(screen):
  for i in range (0, oled_W+1, 4):
    for line in screen:
      oled.text(line[2], -oled_W+i, line[1])
    oled.show()
    if i!= oled_W:
      oled.fill(0)

# Scroll out screen horizontally from left to right
def scroll_out_screen(speed):
  for i in range ((oled_W+1)/speed):
    for j in range (oled_H):
      oled.pixel(i, j, 0)
    oled.scroll(speed,0)
    oled.show()

# Continuous horizontal scroll
def scroll_screen_in_out(screen):
  for i in range (0, (oled_W+1)*2, 1):
    for line in screen:
      oled.text(line[2], -oled_W+i, line[1])
    oled.show()
    if i!= oled_W:
      oled.fill(0)

# Scroll in screen vertically
def scroll_in_screen_v(screen):
  for i in range (0, (oled_H+1), 1):
    for line in screen:
      oled.text(line[2], line[0], -oled_H+i+line[1])
    oled.show()
    if i!= oled_H:
      oled.fill(0)

# Scroll out screen vertically
def scroll_out_screen_v(speed):
  for i in range ((oled_H+1)/speed):
    for j in range (oled_W):
      oled.pixel(j, i, 0)
    oled.scroll(0,speed)
    oled.show()

# Continous vertical scroll
def scroll_screen_in_out_v(screen):
  for i in range (0, (oled_H*2+1), 1):
    for line in screen:
      oled.text(line[2], line[0], -oled_H+i+line[1])
    oled.show()
    if i!= oled_H:
      oled.fill(0)

def main():
    while True:
        
        # Desplazar a la derecha, detenerse y borrar texto
        # Pantalla 1
        scroll_in_screen(screen1)   # escibir texto desplazado a la derecha
        sleep(2)
        scroll_out_screen(4)        # borrar texto desplazado a la derecha
        
        # Pantalla 2
        scroll_in_screen(screen2)
        sleep(2)
        scroll_out_screen(4)

        # Pantalla 3
        scroll_in_screen(screen3)
        sleep(2)
        scroll_out_screen(4)

        # Desplazamiento continuo de pantallas
        scroll_screen_in_out(screen1)
        scroll_screen_in_out(screen2)
        scroll_screen_in_out(screen3)

        # Desplazar vertical, parar y borrar
        # Pantalla 1
        scroll_in_screen_v(screen1)
        sleep(2)
        scroll_out_screen_v(4)

        # Pantalla 2
        scroll_in_screen_v(screen2)
        sleep(2)
        scroll_out_screen_v(4)

        # Pantalla 3
        scroll_in_screen_v(screen3)
        sleep(2)
        scroll_out_screen_v(4)

        # Desplazamiento vertical continuo
        scroll_screen_in_out_v(screen1)
        scroll_screen_in_out_v(screen2)
        scroll_screen_in_out_v(screen3)
    
    oled.poweroff()

if __name__ == "__main__":
    main()
