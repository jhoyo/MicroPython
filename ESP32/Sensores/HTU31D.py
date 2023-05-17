
# Libreria de micropython de ESP32 para HTU31D
from time import sleep, sleep_ms
from math import log10
from machine import Pin, SoftI2C 
from sys import exit

HTU31D_DEFAULT_ADDR   = const(0x40)  # HTU31D default I2C Address
HTU31D_SECONDARY_ADDR = const(0x41)  # HTU31D alternate I2C Address
HTU31D_ADDRESSES      = (HTU31D_DEFAULT_ADDR, HTU31D_SECONDARY_ADDR)

HTU31D_READSERIAL     = const(0x0A)  # Read Out of Serial Register
HTU31D_SOFTRESET      = const(0x1E)  # Soft Reset
HTU31D_HEATERON       = const(0x04)  # Enable heater
HTU31D_HEATEROFF      = const(0x02)  # Disable heater
HTU31D_CONVERSION     = const(0x40)  # Start a conversion
HTU31D_READTEMPHUM    = const(0x00)  # Read the conversion values
HTU31D_READHUM        = const(0x10)  # Read RH conversion
HTU31D_DISGNOSTIC     = const(0x08)  # Read Disgnostic 

HTU31D_HUMIDITY_RES   = ("0.020%", "0.014%", "0.010%", "0.007%")
HTU31D_TEMP_RES       = ("0.040", "0.025", "0.016", "0.012")

class HTU31D:
    
  def __init__(self, i2c, address):
    self.i2c = i2c
    self.address = address
    if address not in HTU31D_ADDRESSES:
      raise ValueError(f"Direccion invalida: {address:#x}")
    self._buffer = bytearray(6)
    self.reset()
    #print(hex(self.readReg(HTU31D_READSERIAL,3))) # leer los 3 bytes del numero serial
    
    print('HTU31D inicializado\n')
  
  def readReg(self, write_address,leng):
    self.i2c.start()
    self.i2c.writeto_mem(self.address,write_address,'')   # comando de leer registro
    self.i2c.stop()
    sleep_ms(50)
    data = bytearray(leng+1)  # numero de bytes a leer
    self.i2c.readfrom_into(self.address,data)

    if self._crc(data):
      l1 = len(data)-1           # numero de bytes de lectura (2 o 3)
      ac = 0
      for i in range(l1):
        ac = ac + (data[i] << 8*(2-i))

      return ac
    else:
      print('error de CRC')
     
  def reset(self):
    #Perform a soft reset of the sensor, resetting all settings to their power-on defaults
    self.i2c.writeto(self.address, bytearray([HTU31D_SOFTRESET]))
    sleep(0.015)
    
  def conversion(self):
    """
    HOSR = 0x00 # 0.020% RH
    HOSR = 0x04 # 0.014% RH
    HOSR = 0x10 # 0.010% RH
    HOSR = 0x14 # 0.007% RH
    
    TOSR = 0x00 # 0.040°C
    TOSR = 0x02 # 0.025°C
    TOSR = 0x04 # 0.016°C
    TOSR = 0x06 # 0.012°C
    """
    HOSR = 0x00
    TOSR = 0x00
    com = HTU31D_CONVERSION | HOSR | TOSR
    self.i2c.writeto(self.address, bytearray([com]))
    
  def measurements(self):
    self.conversion()
    sleep_ms(50)
    self.i2c.start()
    self.i2c.writeto_mem(self.address,HTU31D_READTEMPHUM,'')   # comando de leer registro
    self.i2c.stop()
    sleep_ms(50)
    data = bytearray(6)                           # numero de bytes a leer incluyendo CRC
    self.i2c.readfrom_into(self.address,data)

    data1 = [data[0], data[1], data[2]]
    data2 = [data[3], data[4], data[5]]
    
    temp = 0
    rh = 0
    
    if self._crc(data1):
      l1 = len(data1)-1           # numero de bytes de lectura (2 o 3)
      ac = 0
      for i in range(l1):
        ac = ac + (data1[i] << 8*(1-i))
      temp = -40+165*(ac)/(2**16-1)
    else:
      print('error de CRC en Temperatura')  
      
    if self._crc(data2):
      l1 = len(data2)-1           # numero de bytes de lectura (2 o 3)
      ac = 0
      for i in range(l1):
        ac = ac + (data2[i] << 8*(1-i))
      rh = 100* ac/(2**16-1)
    else:
      print('error de CRC en Humedad Relativa')
      
    return temp, rh
      
  def Humidity(self):
    self.conversion()
    sleep_ms(50)
    data = self.readReg(HTU31D_READHUM,2) >> 8
    return 100 * data / (2**16 - 1)
 
  def heater_on(self):
    self.i2c.writeto(self.address, bytearray([HTU31D_HEATERON]))
    sleep(0.015)

    
  def heater_off(self):
    self.i2c.writeto(self.address, bytearray([HTU31D_HEATEROFF]))
    sleep(0.015)
    
  def diagnostic(self):
    diag = self.readReg(HTU31D_DISGNOSTIC,1)
    if diag & 0x80:
      print("Error en Memoria No Volatil del Sensor")
    if diag & 0x40:
      print("Humedad fuera de rango (0-100), truncada")
    if diag & 0x20:
      print("Humedad arriba de 120%")
    if diag & 0x10:
      print("Humedad abajo de -10%")
    if diag & 0x08:
      print("Temperatura fuera de rango, truncada")
    if diag & 0x04:
      print("Temperatura arriba de 150°C")
    if diag & 0x02:
      print("Temperatura abajo de -50°C")
    if diag & 0x01:
      print("Calentador encendido")
    else:
      print("Calentador apagado")
      
  def serial_number(self):
    self.i2c.start()
    self.i2c.writeto_mem(self.address,HTU31D_READSERIAL,'')   # comando de leer registro
    self.i2c.stop()
    sleep_ms(50)
    data = bytearray(4)                           # numero de bytes a leer incluyendo CRC
    self.i2c.readfrom_into(self.address,data)
    ns = data[0]<<16 | data[1]<<8 | data[2]
    if self._crc(data):
      print("Numero de serie:",hex(ns))
    else:
      print('error de CRC en Numero de Serie')
      
  def partial_pressure(self):   
    # calcula la presion parcial en mmHg a partir de la temperatura ambiente
    temp, rh = self.measurements()
    A=8.1332
    B=1762.39 
    C=235.66
    pp = pow(10, (A - (B/(temp+C))))
    return pp
    
  def dew_point(self):
    temp, rh = self.measurements()
    A=8.1332
    B=1762.39 
    C=235.66
    pp = pow(10, (A - (B/(temp+C))))
    d = log10(rh * pp/100)-A
    td = -((B/d) + C)
    return td

  @staticmethod
  def _crc(value) -> int:
    crc1 = value[len(value)-1]  # obtener el byte de CRC de la lectura del separate
    l1 = len(value)-1           # numero de bytes de lectura (2 o 3)
    ac = 0
    for i in range(l1):
      ac = ac + (value[i] << 8*(2-i)) # convertir bytearray en entero
      
    polynom = 0x988000  # x^8 + x^5 + x^4 + 1
    msb     = 0x800000
    mask    = 0xFF8000
    
    if l1 ==3:
      polynom = polynom << 8
      msb = msb << 8
      mask = mask <<8
      ac = ac << 8
      
    result  = ac #<< 8  # Pad with zeros as specified in spec
    while msb != 0x80:
      # Check if msb of current value is 1 and apply XOR mask
      if result & msb:
        result = ((result ^ polynom) & mask) | (result & ~mask)
      # Shift by one
      msb     >>= 1
      mask    >>= 1
      polynom >>= 1

    if result == crc1:
      return True
    else:
      return False
