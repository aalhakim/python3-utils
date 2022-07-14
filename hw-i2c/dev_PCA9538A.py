"""
PCA9538A 8-Bit I2C GPIO Expander with Interrupt and Reset
"""

from i2c_driver import I2C_Driver


##############################################################################
PCA9538A_REG_ADDR_INPUTS   = 0x00  # Input port value (read-only)
PCA9528A_REG_ADDR_OUTPUTS  = 0x01  # Output port setting
PCA9538A_REG_ADDR_POLARITY = 0x02  # Input port polarity configuration
PCA9538A_REG_ADDR_CONFIG   = 0x03  # Port direction configuration

PORT_COUNT = 8


##############################################################################
class PCA9538A_GPIO_Expander(object):

    def __init__(self, i2c_driver, dev_addr):
        self.i2c = i2c_driver
        self.addr = dev_addr

        # Store register values, initialised to register defaults
        self.reg_config = 0xFF
        self.reg_output = 0xFF
        self.reg_polarity = 0x00

    def _validate_pins(self, pins):
        """Raise error if invalid pin is given"""
        for pin in pins:
            if (pin < 0) or (pin > PORT_COUNT-1):
                raise Exception(
                    "P{} is an invalid pin number. Only pins 0 to {} are allowed"
                    .format(pin, PORT_COUNT)
                )

    def configure(self, io, *pins):
        """Configure pins as inputs or outputs

        Args:
            io <str>: "input" or "output"
            pins <[<int>]>: List of integers representing port numbers
                to configure
        """
        self._validate_pins(pins)   # Raises error if any pin is invalid

        if io == "input":
            for pin in pins:
                self.reg_config |= (1 << pin)


##############################################################################
if __name__ == "__main__":
    pass
