# ina219
# Authors: Ali H Al-Hakim,
# -------------------------
# INA219 BI-DIRECTIONAL CURRENT/POWER MONITOR WITH I2C INTERFACE
# http://www.ti.com/lit/ds/symlink/ina219.pdf


########################################################################
import logging
debugLogger = logging.getLogger(__name__)


########################################################################
from adafruit_i2c import Adafruit_I2C


########################################################################
INA219_REG_ADDR_CONFIG  = 0x00
INA219_REG_ADDR_SHUNT   = 0x01
INA219_REG_ADDR_BUS     = 0x02
INA219_REG_ADDR_POWER   = 0x03
INA219_REG_ADDR_CURRENT = 0x04
INA219_REG_ADDR_CAL     = 0x05


class INA219_PowerMonitor(object):
    def __init__(self, address=0x40, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.address = address
        self.debug = debug

    def setup(self, reg_config=0xBC40, reg_cal=0x0000):
        self.configure(reg_config)
        self.calibrate(reg_cal)

    def configure(self, reg_config=0xBC40,):
        # configuration bits, see data sheet
        configure_ = ((reg_config & 0x00FF) << 8) + (reg_config >> 8)
        self.i2c.write16(INA219_REG_ADDR_CONFIG, configure_)

    def calibrate(self, reg_cal=0x0000):
        calibrate_ = (((reg_cal & 0x00FF) << 8) + (reg_cal >> 8))
        self.i2c.write16(INA219_REG_ADDR_CAL, calibrate_)

    def shunt_voltage(self):
        shunt_voltage_ = self.i2c.readS16(INA219_REG_ADDR_SHUNT, False)
        return shunt_voltage_ * 0.01

    def bus_voltage(self):
        bus_voltage_ = self.i2c.readU16(INA219_REG_ADDR_BUS, False)
        return (bus_voltage_ >> 3) * 4.0

    def current(self, i_lsb):
        r = self.i2c.readU16(INA219_REG_ADDR_BUS, False)

        if (r & 0x0001) == 0x0001:
            if self.debug is True:
                debugLogger.error('Current measurement register overflow')
            return 0

        try:
            current_ = self.i2c.readS16(INA219_REG_ADDR_CURRENT, False)
        except:
            if self.debug is True:
                debugLogger.error('Could not read current from I2C')
            return 0

        return current_ * i_lsb

    def power(self, p_lsb):
        r = self.i2c.readU16(INA219_REG_ADDR_BUS, False)

        if (r & 0x0001) == 0x0001:
            if self.debug is True:
                debugLogger.error('Current measurement register overflow')
            return 0

        try:
            power_ = self.i2c.readU16(INA219_REG_ADDR_POWER, False)
        except:
            if self.debug is True:
                debugLogger.error('Could not read power from I2C')
            return 0

        return power_ * p_lsb
