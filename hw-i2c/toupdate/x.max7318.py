# max7318
# Authors: Ali H Al-Hakim,
# -------------------------
# MAX7318 2-WIRE-INTERFACED, 16-BIT, I/O PORT EXPANDER WITH INTERRUPT AND HOT-INSERTION PROTECTION
# http://datasheets.maximintegrated.com/en/ds/MAX7318.pdf


########################################################################
import logging
debugLogger = logging.getLogger(__name__)


########################################################################
from adafruit_i2c import Adafruit_I2C


########################################################################
MAX7318_INPUT_REG_ADDR = 0x00     # Input port register address, [16 bits]
MAX7318_OUTPUT_REG_ADDR = 0x02    # Output port register address 1, [16 bits]
MAX7318_POLARITY_REG_ADDR = 0x04  # Polarity Inversion register address 1, [16 bits]
MAX7318_CONFIG_REG_ADDR = 0x06    # Configuration register address 1, [16 bits]


class MAX7318_GPIOExpander(object):
    def __init__(self, address=0xFF, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.debug = debug
        self.address = address      # Address of the MAX7318 IC
        self.reg_config = 0xFFFF    # Default setting from datasheet
        self.reg_output = 0xFFFF    # Default setting from datasheet
        self.reg_polarity = 0x0000  # Default setting from datasheet

    def set_to_all_outputs(self):
        self.uninvert_all()
        self.configure('output', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        self.reset_all()

    def set_address(self, address):
        self.address = address
        self.i2c.address = self.address

    def validate_pins(self, pins):
        for pin in pins:
            if (pin < 0) or (pin > 15):
                raise Exception('P{} is an invalid pin number. GPIO pins are indexed 0 to 15 only.'.format(pin))

    def reconfigure(self):
        # Set pins to last known settings
        if self.i2c.readU16(MAX7318_OUTPUT_REG_ADDR, True) != self.reg_output:
            self.i2c.write16(MAX7318_OUTPUT_REG_ADDR, self.reg_output)

        if self.i2c.readU16(MAX7318_POLARITY_REG_ADDR, True) != self.reg_polarity:
            self.i2c.write16(MAX7318_POLARITY_REG_ADDR, self.reg_polarity)

        # Configure the pins as inputs or outputs
        if self.i2c.readU16(MAX7318_CONFIG_REG_ADDR, True) != self.reg_config:
            self.i2c.write16(MAX7318_CONFIG_REG_ADDR, self.reg_config)

    def configure(self, io, *pins):
        # Cancel entire command if any arguments are invalid
        self.validate_pins(pins)
        # Configure input ports
        if io == 'input':
            for pin in pins:
                self.reg_config |= (1 << pin)
        # Configure output ports
        elif io == 'output':
            for pin in pins:
                self.reg_config &= ~(1 << pin)
        # Notify port type error
        else:
            raise Exception('"{}" is not valid. GPIO pins can only be "input" or "output".'.format(io))

        # Set pins to last known settings
        self.i2c.write16(MAX7318_OUTPUT_REG_ADDR, self.reg_output)
        self.i2c.write16(MAX7318_POLARITY_REG_ADDR, self.reg_polarity)
        # Configure the pins as inputs or outputs
        self.i2c.write16(MAX7318_CONFIG_REG_ADDR, self.reg_config)

    # Provides a way to set/reset output pins in the same command
    def configure_outputs(self, set_pins, reset_pins):
        # Cancel entire command if any arguments are invalid
        self.validate_pins(set_pins + reset_pins)
        # Configure the output register data to be sent
        for pin in set_pins:
            self.reg_output |= (1 << pin)
        for pin in reset_pins:
            self.reg_output &= ~(1 << pin)

        self.i2c.write16(MAX7318_OUTPUT_REG_ADDR, self.reg_output)

    def set(self, *pins):
        # Cancel entire command if any arguments are invalid
        self.validate_pins(pins)
        for pin in pins:
            # Check if 'pin' is configured as an input
            if ((1 << pin) & self.reg_config) == (1 << pin):
                debugLogger.warn('P{} is not configured as an output port'.format(pin))
            # Set 'pin'
            self.reg_output |= (1 << pin)

        self.i2c.write16(MAX7318_OUTPUT_REG_ADDR, self.reg_output)

    def reset(self, *pins):
        # Cancel entire command if any arguments are invalid
        self.validate_pins(pins)
        for pin in pins:
            # Check if 'pin' is configured as an input
            if ((1 << pin) & self.reg_config) == (1 << pin):
                debugLogger.warn('P{} is not configured as an output port'.format(pin))
            # Reset 'pin'
            self.reg_output &= ~(1 << pin)

        self.i2c.write16(MAX7318_OUTPUT_REG_ADDR, self.reg_output)

    def invert(self, *pins):
        # Cancel entire command if any arguments are invalid
        self.validate_pins(pins)
        for pin in pins:
            # Check if 'pin' is configured as an output
            if ((1 << pin) & self.reg_config) != (1 << pin):
                debugLogger.warn('P{} is not configured as an input port'.format(pin))
            # Invert 'pin'
            self.reg_polarity |= (1 << pin)

        self.i2c.write16(MAX7318_POLARITY_REG_ADDR, self.reg_polarity)

    def uninvert(self, *pins):
        # Cancel entire command if any arguments are invalid
        self.validate_pins(pins)
        for pin in pins:
            # Check if 'pin' is configured as an output
            if ((1 << pin) & self.reg_config) != (1 << pin):
                debugLogger.warn('P{} is not configured as an input port'.format(pin))
            # Uninvert 'pin'
            self.reg_polarity &= ~(1 << pin)

        self.i2c.write16(MAX7318_POLARITY_REG_ADDR, self.reg_polarity)

    def read(self, *pins):
        # Cancel entire command if any arguments are invalid
        self.validate_pins(pins)
        for pin in pins:
            # Check if 'pin' is configured as an input
            if ((1 << pin) & self.reg_config) == (1 << pin):
                debugLogger.warn('P{} is not configured as an input port'.format(pin))
            # Check if 'pin' is inverted
            if ((1 << pin) & self.reg_polarity) == (1 << pin):
                debugLogger.warn('P{} is inverted'.format(pin))

        return self.i2c.readU16(MAX7318_INPUT_REG_ADDR, True)  # Should return as [15, ..., 0]

    def set_all(self):
        self.set(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        debugLogger.debug('All outputs set')

    def reset_all(self):
        self.reset(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        debugLogger.debug('All outputs reset')

    def invert_all(self):
        self.invert(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        debugLogger.debug('All outputs inverted')

    def uninvert_all(self):
        self.uninvert(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        debugLogger.debug('All outputs uninverted')
