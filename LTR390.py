
from time import sleep, sleep_ms 
from machine import Pin, I2C 
from sys import exit  

ADDR  = const(0X53)  

LTR390_MAIN_CTRL		= const(0x00)  	# Main control register 
LTR390_MEAS_RATE		= const(0x04)  	# Resolution and data rate 
LTR390_GAIN         = const(0x05)  	# ALS and UVS gain range 
LTR390_PART_ID      = const(0x06)  	# Part id/revision register 
LTR390_MAIN_STATUS	= const(0x07)		# Main status register 
LTR390_ALSDATA      = const(0x0D)  	# ALS data lowest byte, 3 byte 
LTR390_UVSDATA      = const(0x10)  	# UVS data lowest byte, 3 byte 
LTR390_INT_CFG      = const(0x19)  	# Interrupt configuration 
LTR390_INT_PST      = const(0x1A)  	# Interrupt persistance config 
LTR390_THRESH_UP    = const(0x21)  	# Upper threshold, low byte, 3 byte 
LTR390_THRESH_LOW   = const(0x24)		# Lower threshold, low byte, 3 byte  

#ALS/UVS measurement resolution, Gain setting, measurement rate 
RESOLUTION_20BIT_TIME400MS  	= const(0X00) 
RESOLUTION_19BIT_TIME200MS  	= const(0X10) 
RESOLUTION_18BIT_TIME100MS  	= const(0X20)	#default 
RESOLUTION_17BIT_TIME50MS   	= const(0x30) 
RESOLUTION_16BIT_TIME25MS   	= const(0x40) 
RESOLUTION_13BIT_TIME12_5MS 	= const(0x50)  

RATE_25MS   	= const(0x0) 
RATE_50MS   	= const(0x1) 
RATE_100MS  	= const(0x2)	# default 
RATE_200MS  	= const(0x3) 
RATE_500MS  	= const(0x4) 
RATE_1000MS 	= const(0x5) 
RATE_2000MS 	= const(0x6)  

# measurement Gain Range. 
GAIN_1  	= const(0x0) 
GAIN_3  	= const(0x1)	# default 
GAIN_6  	= const(0x2) 
GAIN_9  	= const(0x3) 
GAIN_18 	= const(0x4)  

class LTR390():
  def __init__(self, i2c, address=ADDR):
    self.i2c = i2c
    self.address = address
    
    self.ID = self.i2c.readfrom_mem(self.address, LTR390_PART_ID,1)  
    if(self.ID != b'\xb2'):
      print("read ID error!,Check the hardware...")
      return
      
    # reset suave del modulo     
    self.i2c.writeto_mem(self.address, LTR390_MAIN_CTRL, b'\x10')
    sleep(2)
    
    # leer estatus del modulo     
    st = self.i2c.readfrom_mem(self.address, LTR390_MAIN_STATUS, 1)
    print('Estatus del LTR390 es :',ord(st),' \n')
    # bit 5 Power on status      
    # bit 4 ALS/UVS interrupt status (1) int triggered     
    # bit 3 UVS/ALS data status (1) datos nuevos          
    
    self.Resol(18, 100)  # fijar resolucion en 18 bits y frecuencia de conversión en 100ms     
    self.Ganancia(3)              # fijar ganancia en 3          
    
    #self.Write_Byte(LTR390_MAIN_CTRL, 0x02) # MAIN_CTRL=UVS in Active Mode       
    
  def Resol(self, res, rate):
    resol = [13, 16, 17, 18, 19, 20]
    rates = [25, 50, 100, 200, 500, 1000, 2000, 2000]
    c1 = [RESOLUTION_13BIT_TIME12_5MS, RESOLUTION_16BIT_TIME25MS, RESOLUTION_17BIT_TIME50MS, RESOLUTION_18BIT_TIME100MS, RESOLUTION_19BIT_TIME200MS, RESOLUTION_20BIT_TIME400MS]   
    c2 = [RATE_25MS, RATE_50MS, RATE_100MS, RATE_200MS, RATE_500MS, RATE_1000MS, RATE_2000MS, RATE_2000MS]     
    if resol.count(res)>0:
      n1 = resol.index(res)
    else:
      n1 = 3
    if resol.count(rate)>0:
      n2 = rates.index(rate)
    else:
      n2 = 2
    cnf = c1[n1] | c2[n2]
    self.i2c.writeto_mem(self.address, LTR390_MEAS_RATE, bytearray([cnf]))  
      
  def Ganancia(self, gan):
    ganancia = [1, 3, 6, 9, 18]
    if ganancia.count(gan)>0:
      g = ganancia.index(gan)
    else:
      g = 1
    self.i2c.writeto_mem(self.address, LTR390_GAIN, bytearray([g]))
      
  def Gan(self):
    ganancia = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04']
    gan = [1, 3, 6, 9,18]

    g = self.i2c.readfrom_mem(self.address, LTR390_GAIN, 1)
    return gan[ganancia.count(g)]
    
  def Res(self):
    res = [4, 2, 1, 0.5, 0.25, 0.125]
    r = self.i2c.readfrom_mem(self.address, LTR390_MEAS_RATE, 1)
    r1 = int.from_bytes(r, "big") >>4
    return res[r1]
    
  def UVS(self):
    self.i2c.writeto_mem(self.address, LTR390_MAIN_CTRL, b'\x0A')   # UVS in Active Mode     
    self.i2c.writeto_mem(self.address, LTR390_INT_CFG, b'\x34')     # UVS_INT_EN=1, Command=0x34     
    self.i2c.writeto_mem(self.address, LTR390_INT_PST, b'\x10')     # Persistencia de INT     
    Data = self.i2c.readfrom_mem(self.address, LTR390_UVSDATA, 3)   # UVS datos     
    uv = Data[2]*65536 + Data[1]*256 + Data[0]
    return uv/2300
    
  def ALS(self):
    self.i2c.writeto_mem(self.address, LTR390_INT_CFG, b'\x14')   # ALS_INT_EN=1, Command=0x14     
    self.i2c.writeto_mem(self.address, LTR390_MAIN_CTRL, b'\x02') # ALS in Active Mode     
    self.i2c.writeto_mem(self.address, LTR390_INT_PST, b'\x10')   # Persistencia de INT     
    Data = self.i2c.readfrom_mem(self.address, LTR390_ALSDATA, 3) # ALS datos     

    als = Data[2]*65536 + Data[1]*256 + Data[0]
    g1 = self.Gan()
    r1 = self.Res()
    return 0.6*als/(g1*r1)
          

