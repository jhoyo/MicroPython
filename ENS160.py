# modificacion de la libreria DFRobot_ENS160.py 
# para usarse en micropython con el ESP32  
from machine import Pin, I2C 
from time import sleep, sleep_ms  

POLY                = const(0x1D)  	# 0b00011101 = x^8+x^4+x^3+x^2+x^0 (x^8 is implicit) 
ENS160_ADDR         = const(0x53)  	# Default I2C address  
ENS160_REG_PARTID   = const(0x00) 
ENS160_REG_OPMODE   = const(0x10) 
ENS160_REG_CONFIG   = const(0x11) 
ENS160_REG_COMMAND  = const(0x12) 
ENS160_REG_TEMPIN   = const(0x13) 
ENS160_REG_RHIN     = const(0x15) 
ENS160_REG_STATUS   = const(0x20) 
ENS160_REG_AQI      = const(0x21) 
ENS160_REG_TVOC     = const(0x22) 
ENS160_REG_ECO2     = const(0x24) 
ENS160_REG_DATAT    = const(0x30) 
ENS160_REG_DATARH   = const(0x32) 
ENS160_REG_DATAMISR = const(0x38) 
ENS160_REG_GPRWRITE = const(0x40) 
ENS160_REG_GPRREAD  = const(0x48)  

MODE_SLEEP          = const(0x00) 
MODE_IDLE           = const(0x01) 
MODE_STANDARD       = const(0x02) 
MODE_RESET          = const(0xF0) 
_valid_modes 		    = (MODE_SLEEP, MODE_IDLE, MODE_STANDARD, MODE_RESET)    

NORMAL_OP           = const(0x00) 
WARM_UP             = const(0x01) 
START_UP            = const(0x02) 
INVALID_OUT         = const(0x03) 

COMMAND_NOP         = const(0x00) 
COMMAND_CLRGPR      = const(0xCC) 
COMMAND_GETAPPVER   = const(0x0E)  

BIT_CONFIG_INTEN    = 0 
BIT_CONFIG_INTDAT   = 1 
BIT_CONFIG_INTGPR   = 3 
BIT_CONFIG_INT_CFG  = 5 
BIT_CONFIG_INTPOL   = 6  

BIT_DEVICE_STATUS_NEWGPR        = 0 
BIT_DEVICE_STATUS_NEWDAT        = 1 
BIT_DEVICE_STATUS_VALIDITY_FLAG = 2 
BIT_DEVICE_STATUS_STATER        = 6 
BIT_DEVICE_STATUS_STATAS        = 7  

VAL_PART_ID = const(0x160)  

class ENS160():   
  """       
  @brief Define DENS160 basic class       
  @details Drive the gas sensor   
  """    
  
  # Interrupt pin active signal level   
  e_INT_pin_active_low  = 0<<6   # Active low   
  e_INT_pin_active_high = 1<<6   # Active high    
  
  # Interrupt pin output driving mode   
  e_INT_pin_OD = 0<<5   	# Open drain   
  e_INT_pin_PP = 1<<5   	# Push / Pull    
  
  # The status of interrupt pin when new data appear in General Purpose Read Registers   
  e_INT_GPR_drdy_DIS = 0<<3   # Disable   
  e_INT_GPR_drdy_EN  = 1<<3   # Enable    
  
  # The status of interrupt pin when new data appear in DATA_XXX   
  e_INT_data_drdy_DIS = 0<<1   # Disable   
  e_INT_data_drdy_EN  = 1<<1   # Enable    
  
  # Interrupt pin main switch mode   
  e_INT_mode_DIS = 0   # Disable   
  e_INT_mode_EN  = 1   # Enable    
  
  # The sensor operating status   
  e_normal_operation        = 0   # Normal operation;    
  e_warm_up_phase           = 1   # Warm-Up phase;    
  e_initial_start_up_phase	= 2   # Initial Start-Up phase;    
  e_invalid_output          = 3   # Invalid output    
  
  def __init__(self,bus,addr=0x53):     
    self.i2c      = bus     
    self.address  = addr     
    self.status   = (0x00, 0x00, 0x00, 0x00)
    
    self.misr     = 0                           # Mirror of DATA_MISR (0 is hardware default)     
    self.status_flag = self.get_ENS160_status() # The structure class for storing the sensor status, uint8_t 
    
  def begin(self):     
    """!       
    @brief Initialize sensor       
    @return  Return init status       
    @retval True indicate initialization succeed       
    @retval False indicate initialization failed     
    """     
    ret = True     
    # leer el ID del sensor     
    chip_id = self.i2c.readfrom_mem(self.address, ENS160_REG_PARTID, 2)
    
    if VAL_PART_ID != ((chip_id[1] << 8) | chip_id[0]):       
      ret = False     
    self.set_PWR_mode(MODE_STANDARD)  	# poner en modo estandar     
    self.set_INT_mode(0x00)           	# empezar de cero     
    return ret      
    
  def set_PWR_mode(self, mode):     
    """!       
    @brief Configure power mode       
    @param mode Configurable power mode:       
    @n       ENS160_SLEEP_MODE: DEEP SLEEP mode (low power standby)       
    @n       ENS160_IDLE_MODE: IDLE mode (low-power)       
    @n       ENS160_STANDARD_MODE: STANDARD Gas Sensing Modes       
    @n       ENS160_RESET_MODE: RESET mode     
    """     
    modes = (0x00, 0x01, 0x02, 0xf0)     
    if mode in modes:       
      self.i2c.writeto_mem(self.address,ENS160_REG_OPMODE, bytearray([mode]))     
    sleep_ms(20)    
    
  def set_INT_mode(self, mode):     
    """!       
    @brief Interrupt config(INT)       
    @param mode Interrupt mode to be set, perform OR operation on the following to get mode:       
    @n       The interrupt occur when new data appear in DATA_XXX register (can get new measured data): e_INT_mode_DIS, disable interrupt; e_INT_mode_EN, enable interrupt       
    @n       Interrupt pin output driving mode: e_INT_pin_OD, open drain; e_INT_pin_PP, push pull       
    @n       Interrupt pin active level: e_INT_pin_active_low, active low; e_INT_pin_active_high, active high     
    """     
    mode |= (self.e_INT_data_drdy_EN | self.e_INT_GPR_drdy_DIS)     
    self.i2c.writeto_mem(self.address, ENS160_REG_CONFIG, bytearray([mode]))     
    sleep(0.02)
    
  def set_temp_and_hum(self, ambient_temp, relative_humidity):     
    """!       
    @brief Users write ambient temperature and relative humidity into ENS160 for calibration and compensation of the measured gas data.       
    @param ambient_temp Compensate the current ambient temperature, float type, unit: C       
    @param relative_humidity Compensate the current ambient humidity, float type, unit: %rH
    """     
    temp = int((ambient_temp + 273.15) * 64 + 0.5)  # ajustar formato de temperatura ambiente para inicio de lectura     
    rh = int(relative_humidity * 512 + 0.5)         # ajustar formato de HR ambiente para inicio de lectura          
    
    buf0 = temp & 0xFF     
    buf1 = (temp & 0xFF00) >> 8     
    buf2 = rh & 0xFF     
    buf3 = (rh & 0xFF00) >> 8      
    
    self.i2c.writeto_mem(self.address, ENS160_REG_TEMPIN, bytearray([buf0, buf1, buf2, buf3]))
    
  def _send_command(self, mode):     
    """!       
    @brief Sensor GPR clear command and command of obtaining FW version number       
    @param mode Sensor three basic commands:       
    @n       ENS160_COMMAND_NOP: null command
    @n       ENS160_COMMAND_GET_APPVER: Get FW Version Command.
    @n       ENS160_COMMAND_CLRGPR: Clears GPR Read Registers Command.
    """
    modes = (0x00, 0x0e, 0xcc)
    if mode not in modes:
      mode = 0x00     
    # Save the previous mode
    old_mode = self.readfrom_mem(self.address, ENS160_REG_OPMODE, 1)[0]
    
    self.set_PWR_mode(MODE_IDLE);   # commands will only be actioned in IDLE mode (OPMODE 0x01).
    self.i2c.writeto_mem(self.address, ENS160_REG_COMMAND, bytearray([mode]))
    self.set_PWR_mode(old_mode);    # Restore to the previous mode
    
  def get_ENS160_status(self):
    """!
    @brief This API is used to get the sensor operating status
    @return Operating status:
    @n        eNormalOperation: Normal operation;
    @n        eWarmUpPhase: Warm-Up phase;
    @n        eInitialStartUpPhase: Initial Start-Up phase;
    @n        eInvalidOutput: Invalid output
    """
    st = int.from_bytes(self.i2c.readfrom_mem(self.address, ENS160_REG_STATUS,1),'big')
    st1 = st & 0x80 # obtener el estatus de operacion 1 = OPMODE ejecutando
    st2 = st & 0x0c # obtener banderas de validacion
    st3 = st & 0x02 # nueva informacion en los registros DATA_XXX
    st4 = st & 0x01 # nueva informacion en los registros GPR_READx
    
    self.status = (st1, st2, st3, st4) # guardar estatus del sensor
    
    return st2 # regresar banderas de validacion
    
    @property
  def get_AQI(self):
    """!
    @brief Get the air quality index calculated on the basis of UBA
    @return Return value range: 1-5 (Corresponding to five levels of Excellent, Good, Moderate, Poor and Unhealthy respectively)
    """
    return self.i2c.readfrom_mem(self.address, ENS160_REG_AQI, 1)[0]
    
  @property
  def get_TVOC_ppb(self):
    """!
    @brief Get TVOC concentration
    @return Return value range: 0–65000, unit: ppb
    """
    buf = self.i2c.readfrom_mem(self.address, ENS160_REG_TVOC, 2)
    return ((buf[1] << 8) | buf[0])
    
  @property
  def get_ECO2_ppm(self):
    """!
    @brief Get CO2 equivalent concentration calculated according to the detected data of VOCs and hydrogen (eCO2 – Equivalent CO2)
    @return Return value range: 400–65000, unit: ppm
    @note Five levels: Excellent(400 - 600), Good(600 - 800), Moderate(800 - 1000),
    @n                  Poor(1000 - 1500), Unhealthy(> 1500)
    """
    buf = self.i2c.readfrom_mem(self.address, ENS160_REG_ECO2, 2)
    return ((buf[1] << 8) | buf[0])
    
  def _get_MISR(self):
    """!
    @brief Get the current crc check code of the sensor
    @return The current crc check code of the sensor
    """
    return self._read_reg(ENS160_REG_DATAMISR, 1)[0]
    
  def _calc_MISR(self, data):
    """!
    @brief Calculate the current crc check code and compare it with the MISR read from the sensor
    @param data The measured data just obtained from the sensor
    @return The current calculated crc check code
    """
    misr_xor= ( (self.misr<<1) ^ data ) & 0xFF
    if( (self.misr & 0x80) == 0 ):
      self.misr = misr_xor
    else:
      self.misr = misr_xor ^ POLY
    return self.misr
    
  def _write_reg(self, reg, data):
    """!
    @brief writes data to a register
    @param reg register address
    @param data written data
    """
    # Low level register writing, not implemented in base class
    raise NotImplementedError()
    
  def _read_reg(self, reg, length):
    """!
    @brief read the data from the register
    @param reg register address
    @param length read data length
    @return read data list
    """
    # Low level register writing, not implemented in base class
    raise NotImplementedError()
    
class ENS160_I2C(ENS160):
  """!
  @brief Define DFRobot_ENS160_I2C basic class
  @details Use I2C protocol to drive the pressure sensor
  """
  def __init__(self, i2c_addr=0x53):
    """!
    @brief Module I2C communication init
    @param i2c_addr I2C communication address
    @param bus I2C bus
    """
    self._addr = i2c_addr
    self.i2c = I2C(0,scl=Pin(21),sda=Pin(22))
    super(ENS160_I2C, self).__init__()
    
  def _write_reg(self, reg, data):
    """!
    @brief writes data to a register
    @param reg register address
    @param data written data
    """
    if isinstance(data, int):
      data = [data]
    self.i2c.write_i2c_block_data(self._addr, reg, data)
    
  def _read_reg(self, reg, length):
    """!
    @brief read the data from the register
    @param reg register address
    @param length length of data to be read
    @return read data list
    """
    return self.i2c.read_i2c_block_data(self._addr, reg, length) 
