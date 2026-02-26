# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import sys

# Allow overriding frozen modules
sys.path.remove(".frozen")
sys.path.append(".frozen")