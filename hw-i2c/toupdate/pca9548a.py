# pca9546a
# Authors: Ali H Al-Hakim,
# -------------------------
# PCA9548A 8-CHANNEL I2C SWITCH WITH RESET
# http://www.nxp.com/documents/data_sheet/PCA9548A.pdf
# http://www.ti.com/lit/ds/symlink/pca9548a.pdf


########################################################################
import time

from adafruit_i2c import Adafruit_I2C

########################################################################
PCA9546A_ADDR = 0x70
PCA9546A_BUS1 = 0x01
PCA9546A_BUS2 = 0x02
PCA9546A_BUS3 = 0x04
PCA9546A_BUS4 = 0x08
PCA9546A_BUS5 = 0x10
PCA9546A_BUS6 = 0x20
PCA9546A_BUS7 = 0x40
PCA9546A_BUS8 = 0x80



class PCA9548A_I2CSwitch(object):
    def __init__(self, address=PCA9546A_ADDR, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.address = address
        self.debug = debug
        self.all_buses = [1, 2, 3, 4, 5, 6, 7, 8]

    def set_follower_address(self, address):
        self.i2c.set_address(address)
        self.address = address

    def validate_bus(self, bus):
        if (bus < 1) or (bus > 8):
            raise Exception('Bus {} is invalid.\nAvailable I2C buses are 1-8.'.format(bus))

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
            print('I2C Switch 0x{:02X} set to {:04b}b.'.format(self.address, self.i2c.readRaw8()))

    def enable_only_this_bus(self, bus=[-1]):
        self.validate_bus(bus)
        config = self.get_config()
        mask = (1 << bus-1)
        if (mask & config) != mask:
            config = mask
            self.i2c.writeRaw8(config)
        if self.debug is True:
            print('I2C Switch 0x{:02X} set to {:04b}b.'.format(self.address, self.i2c.readRaw8()))

    def disable_bus(self, *buses):
        self.validate_buses(buses)
        config = self.get_config()
        for bus in buses:
            mask = (1 << bus-1)
            if (mask & config) == mask:
                config &= ~mask

        self.i2c.writeRaw8(config)
        if self.debug is True:
            print('I2C Switch 0x{:02X} set to {:04b}b.'.format(self.address, self.i2c.readRaw8()))

    def disable_all(self):
        self.disable_bus(*self.all_buses)

    def get_config(self):
        return self.i2c.readRaw8()
