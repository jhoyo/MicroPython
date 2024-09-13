from machine import Pin, PWM, SoftI2C
from time import sleep
import ssd1306 as ssd1306

i2c = SoftI2C(scl = Pin(22), sda = Pin(21))

oled_W = 128    # ancho de la pantalla en puntos
oled_H = 64     # alto de la pantalla en puntos
oled = ssd1306.SSD1306_I2C(oled_W, oled_H, i2c)

movimiento = False
screen1 = [[0, 0 , "Movimiento detectado!"], [0, 16, "Interrupcion generada por"], [0, 32, "Pin(27)"]]
screen2 = [[0, 0 , " "], [0, 16, "Movimiento termino!"], [0, 32, " "]]

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
    
def interrupcion(pin):
  global movimiento
  movimiento = True
  global pin_interrupcion
  pin_interrupcion = pin 

# Funcion para encender y atenuar el led de salida
# pasos define la duración del tiempo de operacion del led
def dimming(pasos):
    dim = 0
    for i in range(pasos):
        led.duty(dim)
        dim +=int(1023/(pasos-1))#53
        sleep(1)
    led.duty(1023)
    
led = PWM(Pin(13))
led.duty(1023)      # apagar el led, esta conectado en activo en bajo
pir = Pin(27, Pin.IN)

pir.irq(trigger=Pin.IRQ_RISING, handler=interrupcion)

while True:
  if movimiento:
    # Desplazar a la derecha, detenerse y borrar texto
    # Pantalla 1
    scroll_in_screen(screen1)   # escibir texto desplazado a la derecha
    sleep(2)
    scroll_out_screen(4)        # borrar texto desplazado a la derecha
    print('Movimiento detectado! interrupcion generada por el pin:', pin_interrupcion)
    dimming(20)
    print('Movimiento termino!\n')
    scroll_in_screen(screen2)   # escibir texto desplazado a la derecha
    sleep(2)
    scroll_out_screen(4)        # borrar texto desplazado a la derecha
    
    movimiento = False