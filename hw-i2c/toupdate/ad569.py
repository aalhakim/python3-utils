# ad569
# Authors: Finlay Kerr, Ali H Al-Hakim,
# -------------------------
# TINY 16-/14-/12-BIT I2C NANDAC+, WITH +/-2LSB inl (16-BIT) AND 2 PPM/DEGC REFERENCE
# http://www.analog.com/media/en/technical-documentation/data-sheets/AD5693R_5692R_5691R_5693.pdf


########################################################################
import logging
debugLogger = logging.getLogger(__name__)


########################################################################
from adafruit_i2c import Adafruit_I2C
import time


########################################################################
AD5691R_REG_ADDR_WRITE_INPUT = 0x10
AD5691R_REG_ADDR_UPDATE_DAC = 0x20
AD5691R_REG_ADDR_WRITE_DAC = 0x30
AD5691R_REG_ADDR_WRITE_CONTROL = 0x40

# Actual possible addresses of AD5691R:
#   0x4C
#   0x4E
# The MightyWatt programmable load is configured with 0x4C

class AD5691R_DAC(object):
    def __init__(self, address=0x00, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.address = address
        self.debug = debug

    def setup(self):
        # Reset the AD5691R to it's defaults
        self.reset()
        # Set the output DAC to 0 ('off')
        self.off()

    def set_address(self, address):
        self.address = address
        self.i2c.address = address

    def swap_bytes(self, word):
        """
        Swap the LSB and MSB bytes of ``word`` around. Necessary for
        some I2C communication, depending on how the follower interprets
        data i.e. little endian or big endian
        """
        funny_word = ((word << 8) & 0xFF00) + (word >> 8)
        return funny_word

    def log(self, message, level="warn"):
        if self.debug:
            if level == "debug":
                debugLogger.debug(message)
            elif level == "info":
                debugLogger.info(message)
            elif level == "warn":
                debugLogger.info(message)
            elif level == "error":
                debugLogger.error(message)
            else:
                debugLogger.warn(message)

    def valid_word(self, word):
        """
        Make sure the ``word`` is within the expected (can actually be
        used) range of the AD5691R.

        The acceptable range is any 12-bit number when shifted 4 bits to
        the left - because the AD5691R interprets bits [15:4].
        """
        minimum_value = 0x000
        maximum_value = 0xFFF
        good_word = word >> 4

        if (good_word >= minimum_value and good_word <= maximum_value):
            return True
        else:
            return False

    def preload(self, value):
        """
        Writes ``value`` to the Input Register.

        The Input Register is used to pre-load the DAC with a value that
        can be later written to the Update DAC Register (which is when
        the output will actually change).

        Call self.update() to write the pre-loaded value into the DAC
        Register.
        """
        # The AD5691R ignores the 4 LSB so a bit shift is needed
        value = value << 4
        # Validate the value range
        if not self.valid_word(value):
            self.log(
                "'{}' is not within the expected range. "
                "Action cancelled.".format(value>>4)
                )
            return
        # The AD5691R requires byte-swapped words
        value = self.swap_bytes(value)
        # Write to the input (pre-load) register
        self.i2c.write16(AD5691R_REG_ADDR_WRITE_INPUT, value)

    def update(self):
        """
        Writes the value in the Input (pre-load) register to the Update
        DAC Register, which updates the DAC output pin.
        """
        # Write to the update register - the value doesn't matter
        self.i2c.write16(AD5691R_REG_ADDR_UPDATE_DAC, 0x00)

    def write(self, value):
        """
        Writes ``value`` to the Write DAC Register.

        This will write ``value`` to both the Input Register and the
        Update DAC Register, which will therefore also update the DAC
        output immediately.
        """
        # The AD5691R ignores the 4 LSB so a bit shift is needed
        value = value << 4
        # Validate the value range
        if not self.valid_word(value):
            self.log(
                "'{}' is not within the expected range. "
                "Action cancelled.".format(value>>4)
                )
            return
        # The AD5691R requires byte-swapped words
        value = self.swap_bytes(value)
        # Write to the input (pre-load) register
        self.i2c.write16(AD5691R_REG_ADDR_WRITE_DAC, value)

    def configure(self, value):
        """
        Writes ``value`` to the Control Register

        The Control Register is 16-bit, but only the top 5 bits have
        function. All other bits should be zeroes (0).

        -----------------------------------------------------
        |  15   |  14  |  13  |  12  |  11  |      10:0     |
        -----------------------------------------------------
        | RESET |   PD MODE   |  REF | GAIN | 000 0000 0000 |
        -----------------------------------------------------

            RESET: Reset the output and all settings to default

            PD MODE: Power Down mode settings
                00: Normal DAC mode
                01: PD1: 1 kOhm output impedance on DAC output
                02: PD1: 100 kOhm output impedance on DAC output
                03: PD1: Tri-State output impedance on DAC output

            REF: Enable or disable the internal reference to reduce
                 power consumption.

            GAIN: Select the gain of the output amplifier
                0: 0V to   V_REF = 2.5V
                1: 0V to 2*V_REF = 5.0V

        Acceptable values of ``value``:
            0x0000<<8 to 0x1F<<8


        """
        # The AD5691R requires byte-swapped words
        value = self.swap_bytes(value)
        # Write to the input (pre-load) register
        try:
            self.i2c.write16(AD5691R_REG_ADDR_WRITE_CONTROL, value)
        except IOError:
            self.log("I think the DAC has been reset, but maybe it's not...")

    def reset(self):
        """
        Write 1 to the software reset bit in the control register
        """
        reset_word = 1 << 15
        self.configure(reset_word)

    def off(self):
        """
        Write ``0`` to the Write DAC Register to turn the output off.

        (INVESTIGATE THE USE OF POWER DOWN MODES TO BETTER DISABLE
         THE OUTPUT)
        """
        self.write(0)

    def on(self, value=0):
        """
        Write ``value`` to the Write DAC Register.
        """
        self.write(value)

    def read_dac(self):
        """
        Read and return the value stored in the DAC Register.

        The read value must be bit-shifted right by four bits, because
        the Write DAC Register of the AD5691R only interprets bits
        [15:4] (i.e. ignores [3:0])
        """
        dac_value = self.i2c.readU16(AD5691R_REG_ADDR_WRITE_DAC, False)
        return dac_value >> 4

    def read_control(self):
        """
        Read and return the value stored in the Control Register.
        """
        control_value = self.i2c.readU16(AD5691R_REG_ADDR_WRITE_CONTROL, False)
        return control_value
