#!/usr/bin/env python3
"""
LM75BD Temperature Monitor Device
"""

# Local library imports
from i2c_driver import I2C_Driver


########################################################################
# Register List
LM75BD_REG_ADDR_TEMP = 0x00  # Temperature measurement
LM75BD_REG_ADDR_CONFIG = 0x01  # Configuration
LM75BD_REG_ADDR_HYSTERESIS = 0x02  # Hysteresis config
LM75BD_REG_ADDR_OVERTEMP = 0x03  # Overtemperature shutdown threshold


########################################################################
class LM75BD_I2C_Temperature_Monitor(object):
    def __init__(self, dev_addr, i2c_driver: I2C_Driver):
        self.addr = dev_addr
        self._i2c = i2c_driver

        self.reg_data = {
            LM75BD_REG_ADDR_TEMP: 0x00,
            LM75BD_REG_ADDR_CONFIG: 0x00,
            LM75BD_REG_ADDR_HYSTERESIS: 0x00,
            LM75BD_REG_ADDR_OVERTEMP: 0x00,
        }

    def _i2c_read(self, reg_addr):
        """Send read command to reg_addr

        Args:
            reg_addr <int>: Register address to write to.

        Raises:
            IOError: May be raised if write_byte_to_reg fails.

        Returns:
            <int>: Read data result
        """
        data = self._i2c.read_word_from_reg(self.addr, reg_addr)
        self.reg_data[reg_addr] = data
        return data

    def init(self):
        """Load current status of device registers"""
        for reg in self.reg_data.keys():
            self.reg_data[reg] = self._i2c_read(reg)

    def get_config(self):
        """Read settings stored in configuration register"""
        return self._i2c.read_byte_from_reg(self.addr, LM75BD_REG_ADDR_CONFIG)

    def set_config(self, new_config):
        """Write new settings to configuration registers"""
        if new_config != self.config:
            # Only send command if there are some changes
            try:
                self._i2c.write_byte_to_reg(
                    self.addr, LM75BD_REG_ADDR_CONFIG, new_config
                )
            except IOError:
                pass
            else:
                self.config = new_config

    def get_temp(self):
        """Read value from temperature register and return as signed bit value

        The temperature register consists of 2 bytes where the 5 LS bits can
        be discarded. The reading is signed 2s complement thus represents a
        positive or negative temperature reading. Each bit represents 0.125 degC.
        """
        temp = self._i2c_read(LM75BD_REG_ADDR_TEMP)

        # Swap MSB and LSB and remove 5 unused LSB
        temp = ((temp << 8) & 0xFF00) + (temp >> 8)
        temp = temp >> 5

        # Convert 11-bit 2s complement to negative value
        if temp > 1023:
            temp -= 2048

        return temp

    def get_temp_in_degC(self):
        """Read value from temperature register and return as degC value"""
        return self.get_temp() * 0.125


########################################################################
if __name__ == "__main__":

    I2C_BUS = 1
    DEVICE_ADDR = 0x48
    DEBUG = False

    # Define an I2C driver instance
    i2c_driver = I2C_Driver(I2C_BUS, debug=DEBUG)

    # Define an I2C peripheral instance
    dev = LM75BD_I2C_Temperature_Monitor(DEVICE_ADDR, i2c_driver)
    print(f"  Config: 0x{dev.config:02X}")
    print("    Temp: {:3.3f} degC".format(dev.get_temp_in_degC()))
