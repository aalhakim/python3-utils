#!/usr/bin/env python3
"""
PCA9538A 8-Bit I2C GPIO Expander with Interrupt and Reset
"""

# Local library imports
from i2c_driver import I2C_Driver


########################################################################
class I2C_GPIO_Expander(object):

    # Must be assigned by child class.
    _i2c_write_method = None  # <I2C_Driver.method>
    _i2c_read_method = None  # <I2C_Driver.method>

    input_reg_addr = None  # <int>
    output_reg_addr = None  # <int>
    polarity_reg_addr = None  # <int>
    config_reg_addr = None  # <int>

    def __init__(self, dev_addr, registers, ports, i2c_driver: I2C_Driver):
        self.addr = dev_addr
        self._i2c = i2c_driver
        self.all_pins = [*range(ports)]
        self.ports = ports
        # Store register values, initialised to default state where possible
        self.reg_data = {reg: state for reg, state in registers}

    def _validate_pins(self, pins):
        """Raise error if invalid pin is given

        Args:
            pins <"""
        for pin in pins:
            if (pin < 0) or (pin > self.ports - 1):
                err_msg = f"P{pin} is an invalid pin number. Only pins 0 to {self.port_count} are allowed"
                raise Exception(err_msg)

    def _is_input(self, pin):
        """Check if `pin` is configured as an input

        Args:
            pin <int>: pin number

        Returns:
            <Boolean>. True if pin is an input, else False.
        """
        assert (
            self.config_reg_addr is not None
        ), "self.config_reg_addr must be assigned a valid value."

        config_reg = self.reg_data[self.config_reg_addr]
        if ((1 << pin) & config_reg) == (1 << pin):
            return True
        else:
            return False

    def _i2c_write(self, reg_addr, data):
        """Write data to reg_addr command register

        Args:
            reg_addr <int>: Register address to write to.
            data <int>: Data value being written

        Raises:
            IOError: May be raised if write_byte_to_reg fails.
        """
        assert (
            self._i2c_write_method is not None
        ), "self._i2c_write_method must be assigned a valid I2C_Driver method."
        self._i2c_write_method(self.addr, reg_addr, data)
        self.reg_data[reg_addr] = data

    def _i2c_read(self, reg_addr):
        """Send read command to reg_addr

        Args:
            reg_addr <int>: Register address to write to.

        Raises:
            IOError: May be raised if write_byte_to_reg fails.

        Returns:
            <int>: Read data result
        """
        assert (
            self._i2c_read_method is not None
        ), "self._i2c_read_method must be assigned a valid I2C_Driver method."
        data = self._i2c_read_method(self.addr, reg_addr)
        self.reg_data[reg_addr] = data
        return data

    def init(self):
        """Load current status of device registers"""
        for reg in self.reg_data.keys():
            self.reg_data[reg] = self._i2c_read(reg)

    def configure(self, io, *pins):
        """Configure pins as inputs or outputs

        Args:
            io <str>: "input" or "output"
            pins <list[int]>: list of integers representing port numbers
                to configure
        """
        assert (
            self.config_reg_addr is not None
        ), "self.config_reg_addr must be assigned a valid value."
        self._validate_pins(pins)

        reg = self.config_reg_addr
        new_cfg = self.reg_data[reg]

        # Configure ports
        if io == "input":
            for pin in pins:
                new_cfg |= 1 << pin
        elif io == "output":
            for pin in pins:
                new_cfg &= ~(1 << pin)
        else:
            err_msg = f"'{io}' is not a valid pin io type. Use 'input' or 'ouput'."
            raise Exception(err_msg)

        self._i2c_write(reg, new_cfg)

    def reconfigure(self):
        """Apply last known settings to all writeable command registers"""
        for reg, cfg in self.reg_data:
            self._i2c_write(reg, cfg)

    def enable(self, *pins):
        """Set pin output to logic high state

        This will not work if the pin is not configured as an output.

        Args:
            pins <list[int]>: list of pins to enable.
        """
        assert (
            self.output_reg_addr is not None
        ), "self.output_reg_addr must be assigned a valid value."
        self._validate_pins(pins)

        reg = self.output_reg_addr
        new_cfg = self.reg_data[reg]

        for pin in pins:
            new_cfg |= 1 << pin
            if self._is_input(pin):
                print(
                    f" >> WARN: You have tried to enable pin {pin} but it is not configured as an output."
                )

        self._i2c_write(reg, new_cfg)

    def disable(self, *pins):
        """Set pin output to logic low state

        This will not work if the pin is not configured as an output.

        Args:
            pins <list[int]>: list of pins to enable.
        """
        assert (
            self.output_reg_addr is not None
        ), "self.output_reg_addr must be assigned a valid value."
        self._validate_pins(pins)

        reg = self.output_reg_addr
        new_cfg = self.reg_data[reg]

        for pin in pins:
            new_cfg &= ~(1 << pin)
            if self._is_input(pin):
                print(
                    f" >> WARN: You have tried to disable pin {pin} but it is not configured as an output."
                )

        self._i2c_write(reg, new_cfg)

    def invert(self, *pins):
        """Invert read value for the given pins

        Args:
            pins <list[int]>: list of pins to enable.
        """
        assert (
            self.polarity_reg_addr is not None
        ), "self.polarity_reg_addr must be assigned a valid value."
        self._validate_pins(pins)

        reg = self.polarity_reg_addr
        new_cfg = self.reg_data[reg]

        for pin in pins:
            new_cfg |= 1 << pin
            if self._is_input(pin):
                print(
                    f" >> WARN: You have inverted pin {pin} but it is not configured as an input."
                )

        self._i2c_write(reg, new_cfg)

    def uninvert(self, *pins):
        """Uninvert read value for the given pins

        This will not work if the pin is not configured as an output.

        Args:
            pins <list[int]>: list of pins to enable.
        """
        assert (
            self.polarity_reg_addr is not None
        ), "self.polarity_reg_addr must be assigned a valid value."
        self._validate_pins(pins)

        reg = self.polarity_reg_addr
        new_cfg = self.reg_data[reg]

        for pin in pins:
            new_cfg &= ~(1 << pin)
            if self._is_input(pin):
                print(
                    f" >> WARN: You have uninverted pin {pin} but it is not configured as an input."
                )

        self._i2c_write(reg, new_cfg)

    def read(self, *pins):
        """Read logic-levels on input pins.

        Args:
            pins <listlist[int]>: list of pins to read from

        Returns:
            Key-value pair in format {pin: state}
        """
        assert (
            self.input_reg_addr is not None
        ), "self.input_reg_addr must be assigned a valid value."
        self._validate_pins(pins)

        data = self._i2c_read(self.input_reg_addr)
        result = {}

        for pin in pins:
            result[pin] = (1 << pin) & data == (1 << pin)
            # Check selected pins are configured as inputs
            if not self._is_input(pin):
                print(
                    " >> WARN: You have read from pin {pin} but it is not configured as an input."
                )

        return result

    def enable_all(self):
        self.enable(*self.all_pins)

    def disable_all(self):
        self.disable(*self.all_pins)

    def invert_all(self):
        self.invert(*self.all_pins)

    def uninvert_all(self):
        self.uninvert(*self.all_pins)

    def read_all(self):
        self.read(*self.all_pins)


########################################################################
if __name__ == "__main__":

    I2C_BUS = 1
    DEVICE_ADDR = 0x70
    DEBUG = False

    # Define an I2C driver instance
    i2c_driver = I2C_Driver(I2C_BUS, DEBUG)

    # Define an I2C
    dev = I2C_GPIO_Expander(DEVICE_ADDR, i2c_driver)
    print(dev.read_all)
