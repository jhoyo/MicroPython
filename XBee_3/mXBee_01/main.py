# Default template for Digi projects
from machine import Pin
from time import sleep

# definicion de terminales
L1 = Pin("D0", Pin.OUT, value=1)    # led menos significativo
L2 = Pin("D2", Pin.OUT, value=1)    # led mas significativo

def main():
    for x in range(5):
        print("Leds 00")
        L1.value(1)
        L2.value(1)
        sleep(2)

        print("Leds 01")
        L1.value(0)
        L2.value(1)
        sleep(2)

        print("Leds 10")
        L1.value(1)
        L2.value(0)
        sleep(2)

        print("Leds 11")
        L1.value(0)
        L2.value(0)
        sleep(2)

    print('Apagando LEDS')
    L1.value(1)
    L2.value(1)

if __name__ == "__main__":
    main()
