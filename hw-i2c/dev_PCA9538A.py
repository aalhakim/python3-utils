#!/usr/bin/env python3
"""
PCA9538A 8-Bit I2C GPIO Expander with Interrupt and Reset
"""

# Local library imports
from i2c_driver import I2C_Driver
from i2c_gpio_expander import I2C_GPIO_Expander


########################################################################
PCA9538A_REG_ADDR_INPUTS = 0x00  # Input port value (read-only)
PCA9538A_REG_ADDR_OUTPUTS = 0x01  # Output port setting
PCA9538A_REG_ADDR_POLARITY = 0x02  # Input port polarity configuration
PCA9538A_REG_ADDR_CONFIG = 0x03  # Port direction configuration

PCA9538A_REGISTER_STATES = {
    PCA9538A_REG_ADDR_INPUTS: 0x00,
    PCA9538A_REG_ADDR_OUTPUTS: 0xFF,
    PCA9538A_REG_ADDR_POLARITY: 0x00,
    PCA9538A_REG_ADDR_CONFIG: 0xFF,
}

PCA9538A_PORT_COUNT = 8


class PCA9538A_GPIO_Expander(I2C_GPIO_Expander):
    def __init__(self, dev_addr, i2c_driver: I2C_Driver):
        super.__init__(
            dev_addr, PCA9538A_REGISTER_STATES, PCA9538A_PORT_COUNT, i2c_driver
        )

        self._i2c_write_method = i2c_driver.write_byte_to_reg
        self._i2c_read_method = i2c_driver.read_byte_from_reg

        self.input_reg_addr = PCA9538A_REG_ADDR_INPUTS
        self.output_reg_addr = PCA9538A_REG_ADDR_OUTPUTS
        self.polarity_reg_addr = PCA9538A_REG_ADDR_POLARITY
        self.config_reg_addr = PCA9538A_REG_ADDR_CONFIG


########################################################################
if __name__ == "__main__":

    I2C_BUS = 1
    DEVICE_ADDR = 0x70
    DEBUG = False

    # Define an I2C driver instance
    i2c_driver = I2C_Driver(I2C_BUS, DEBUG)

    # Define an I2C
    dev = PCA9538A_GPIO_Expander(DEVICE_ADDR, i2c_driver)
    print(dev.read_all())
