# pca9546a
# Authors: Ali H Al-Hakim,
# -------------------------
# PCA9546A 4-CHANNEL I2C SWITCH WITH RESET
# http://www.nxp.com/documents/data_sheet/PCA9546A.pdf


########################################################################
import logging
debugLogger = logging.getLogger(__name__)


########################################################################
from adafruit_i2c import Adafruit_I2C
import time
import os


########################################################################
PCA9546A_ADDR = 0x70
PCA9546A_BUS1 = 0x01
PCA9546A_BUS2 = 0x02
PCA9546A_BUS3 = 0x04
PCA9546A_BUS4 = 0x08


class PCA9546A_I2CSwitch(object):
    def __init__(self, address=PCA9546A_ADDR, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.address = address
        self.debug = debug
        self.all_buses = [1, 2, 3, 4]

    def set_follower_address(self, address):
        self.i2c.set_address(address)
        self.address = address

    def validate_bus(self, bus):
        if (bus < 1) or (bus > 4):
            raise Exception('Bus {} is invalid.\nAvailable I2C buses are 1-4.'.format(bus))

    def validate_buses(self, buses):
        for bus in buses:
            self.validate_bus(bus)

    def enable_bus(self, *buses):
        self.validate_buses(buses)
        config = self.get_config()
        for bus in buses:
            mask = (1 << bus-1)
            if (mask & config) != mask:
                config |= mask

        self.i2c.writeRaw8(config)
        if self.debug is True:
            debugLogger.debug('I2C Switch 0x{:02X} set to {:04b}b.'.format(self.address, self.i2c.readRaw8()))

    def enable_only_this_bus(self, bus=[-1]):
        self.validate_bus(bus)
        config = self.get_config()
        mask = (1 << bus-1)
        if (mask & config) != mask:
            config = mask
            self.i2c.writeRaw8(config)
        if self.debug is True:
            debugLogger.debug('I2C Switch 0x{:02X} set to {:04b}b.'.format(self.address, self.i2c.readRaw8()))

    def disable_bus(self, *buses):
        self.validate_buses(buses)
        config = self.get_config()
        for bus in buses:
            mask = (1 << bus-1)
            if (mask & config) == mask:
                config &= ~mask

        self.i2c.writeRaw8(config)
        if self.debug is True:
            debugLogger.debug('I2C Switch 0x{:02X} set to {:04b}b.'.format(self.address, self.i2c.readRaw8()))

    def disable_all(self):
        self.disable_bus(*self.all_buses)

    def get_config(self):
        return self.i2c.readRaw8()
