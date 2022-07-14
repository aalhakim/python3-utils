"""
PCA9538A 8-Bit I2C GPIO Expander with Interrupt and Reset
"""

from i2c_driver import I2C_Driver, DEFAULT_I2C_BUS


########################################################################
PCA9538A_REG_ADDR_INPUTS   = 0  # Input port value (read-only)
PCA9538A_REG_ADDR_OUTPUTS  = 1  # Output port setting
PCA9538A_REG_ADDR_POLARITY = 2  # Input port polarity configuration
PCA9538A_REG_ADDR_CONFIG   = 3  # Port direction configuration

PORT_COUNT = 8
ALL_PINS = [*range(PORT_COUNT)]


########################################################################
class PCA9538A_GPIO_Expander(object):

    def __init__(self, dev_addr, i2c_driver=I2C_Driver(DEFAULT_I2C_BUS)):
        self.addr = dev_addr
        self._i2c = i2c_driver

        # Store register values, initialised to register defaults
        self.reg_data = {
            PCA9538A_REG_ADDR_OUTPUTS: 0xFF,
            PCA9538A_REG_ADDR_POLARITY: 0x00,
            PCA9538A_REG_ADDR_CONFIG: 0xFF
        }

    def _validate_pins(self, pins):
        """Raise error if invalid pin is given

        Args:
            pins <"""
        for pin in pins:
            if (pin < 0) or (pin > PORT_COUNT-1):
                err_msg = f"P{pin} is an invalid pin number. Only pins 0 to {PORT_COUNT} are allowed"
                raise Exception(err_msg)

    def _is_input(self, pin):
        """Check if `pin` is configured as an input

        Args:
            pin <int>: pin number

        Returns:
            <Boolean>. True if pin is an input, else False.
        """
        config_reg = self.reg_data[PCA9538A_REG_ADDR_CONFIG]
        if ((1 << pin) & config_reg) == (1 << pin):
            return True
        else:
            return False

    def _update_reg(self, reg_addr, data):
        """Write data to reg_addr command register

        Args:
            reg_addr <int>: Register address to write to.
            data <int>: Data value being written

        Raise:
            IOError: May be raised if write_byte_to_reg fails.
        """
        self._i2c.write_byte_to_reg(self.addr, reg_addr, data)
        self.reg_data[reg_addr] = data


    def configure(self, io, *pins):
        """Configure pins as inputs or outputs

        Args:
            io <str>: "input" or "output"
            pins <list[int]>: list of integers representing port numbers
                to configure
        """
        self._validate_pins(pins)

        reg = PCA9538A_REG_ADDR_CONFIG
        new_cfg = self.reg_data[reg]

        # Configure ports
        if io == "input":
            for pin in pins:
                new_cfg |= (1 << pin)
        elif io == "output":
            for pin in pins:
                new_cfg &= ~(1 << pin)
        else:
            err_msg = f"'{io}' is not a valid pin io type. Use 'input' or 'ouput'."
            raise Exception(err_msg)

        self._update_reg(reg, new_cfg)

    def enable(self, *pins):
        """Set pin output to logic high state

        This will not work if the pin is not configured as an output.

        Args:
            pins <list[int]>: list of pins to enable.
        """
        self._validate_pins(pins)

        reg = PCA9538A_REG_ADDR_OUTPUTS
        new_cfg = self.reg_data[reg]

        for pin in pins:
            new_cfg |= (1 << pin)
            if self._is_input(pin):
                print(f" >> WARN: You have tried to enable pin {pin} but it is not configured as an output.")

        self._update_reg(reg, new_cfg)

    def disable(self, *pins):
        """Set pin output to logic low state

        This will not work if the pin is not configured as an output.

        Args:
            pins <list[int]>: list of pins to enable.
        """
        self._validate_pins(pins)

        reg = PCA9538A_REG_ADDR_OUTPUTS
        new_cfg = self.reg_data[reg]

        for pin in pins:
            new_cfg &= ~(1 << pin)
            if self._is_input(pin):
                print(f" >> WARN: You have tried to disable pin {pin} but it is not configured as an output.")

        self._update_reg(reg, new_cfg)

    def invert(self, *pins):
        """Invert read value for the given pins

        Args:
            pins <list[int]>: list of pins to enable.
        """
        self._validate_pins(pins)

        reg = PCA9538A_REG_ADDR_POLARITY
        new_cfg = self.reg_data[reg]

        for pin in pins:
            new_cfg |= (1 << pin)
            if self._is_input(pin):
                print(f" >> WARN: You have inverted pin {pin} but it is not configured as an input.")

        self._update_reg(reg, new_cfg)

    def uninvert(self, *pins):
        """Uninvert read value for the given pins

        This will not work if the pin is not configured as an output.

        Args:
            pins <list[int]>: list of pins to enable.
        """
        self._validate_pins(pins)

        reg = PCA9538A_REG_ADDR_POLARITY
        new_cfg = self.reg_data[reg]

        for pin in pins:
            new_cfg &= ~(1 << pin)
            if self._is_input(pin):
                print(f" >> WARN: You have uninverted pin {pin} but it is not configured as an input.")

        self._update_reg(reg, new_cfg)

    def read(self, *pins):
        """Read logic-levels on input pins.

        Args:
            pins <listlist[int]>: list of pins to read from

        Returns:
            Key-value pair in format {pin: state}
        """
        self._validate_pins(pins)

        data = self._i2c.read_byte_from_reg(self.addr, PCA9538A_REG_ADDR_INPUTS)
        result = {}

        for pin in pins:
            result[pin] = (1 << pin) & result == (1 << pin)
            # Check selected pins are configured as inputs
            if not self._is_input(pin):
                print(" >> WARN: You have read from pin {pin} but it is not configured as an input.")

        return self._i2c.read_byte_from_reg(self.addr, PCA9538A_REG_ADDR_INPUTS)

    def enable_all(self):
        self.set(*ALL_PINS)

    def disable_all(self):
        self.reset(*ALL_PINS)

    def invert_all(self):
        self.invert(*ALL_PINS)

    def uninvert_all(self):
        self.uninvert(*ALL_PINS)

    def read_all(self):
        self.read()


########################################################################
if __name__ == "__main__":

    I2C_BUS = 1
    DEVICE_ADDR = 0x70
    DEBUG = False

    # Define an I2C driver instance
    i2c_driver = I2C_Driver(I2C_BUS, DEBUG)

    # Define an I2C
    dev = PCA9538A_GPIO_Expander(DEVICE_ADDR, i2c_driver)
    print(dev.read_all)
