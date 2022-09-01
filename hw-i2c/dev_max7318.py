#!/usr/bin/env python3
"""
MAX7318 16-Bit I2C GPIO Expander
"""

# Local library imports
from i2c_driver import I2C_Driver
from i2c_gpio_expander import I2C_GPIO_Expander


########################################################################
MAX7318_REG_ADDR_INPUTS = 0x00  # Input port value (read-only)
MAX7318_REG_ADDR_OUTPUTS = 0x02  # Output port setting
MAX7318_REG_ADDR_POLARITY = 0x04  # Input port polarity configuration
MAX7318_REG_ADDR_CONFIG = 0x06  # Port direction configuration

MAX7318_REGISTER_STATES = {
    MAX7318_REG_ADDR_INPUTS: 0x0000,
    MAX7318_REG_ADDR_OUTPUTS: 0xFFFF,
    MAX7318_REG_ADDR_POLARITY: 0x0000,
    MAX7318_REG_ADDR_CONFIG: 0xFFFF,
}

MAX7318_PORT_COUNT = 16


class MAX7318_GPIO_Expander(I2C_GPIO_Expander):
    def __init__(self, dev_addr, i2c_driver: I2C_Driver):
        super.__init__(
            dev_addr, MAX7318_REGISTER_STATES, MAX7318_PORT_COUNT, i2c_driver
        )

        self._i2c_write_method = i2c_driver.write_word_to_reg
        self._i2c_read_method = i2c_driver.read_word_from_reg

        self.input_reg_addr = MAX7318_REG_ADDR_INPUTS
        self.output_reg_addr = MAX7318_REG_ADDR_OUTPUTS
        self.polarity_reg_addr = MAX7318_REG_ADDR_POLARITY
        self.config_reg_addr = MAX7318_REG_ADDR_CONFIG


########################################################################
if __name__ == "__main__":

    I2C_BUS = 1
    DEVICE_ADDR = 0x70
    DEBUG = False

    # Define an I2C driver instance
    i2c_driver = I2C_Driver(I2C_BUS, DEBUG)

    # Define an I2C
    dev = MAX7318_GPIO_Expander(DEVICE_ADDR, i2c_driver)
    print(dev.read_all())
