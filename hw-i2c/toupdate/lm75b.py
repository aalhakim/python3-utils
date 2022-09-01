"""
Python driver module for the NXP LM75B Digital temperature sensor and
thermal watchdog

(Apr 2017)
Product Page: http://www.nxp.com/products/interfaces/ic-bus-portfolio/ic-temperature-voltage-monitors/digital-temperature-sensor-and-thermal-watchdog:LM75B
Datasheet: http://www.nxp.com/documents/data_sheet/LM75B.pdf
"""
from adafruit_i2c import Adafruit_I2C


########################################################################
LM75B_DEV_ADDRESS = 0x49  # 0x48 in some cases?

LM75B_REG_ADDR_TEMP = 0x00          # Temperature Measurement Register
LM75B_REG_ADDR_CONFIG = 0x01        # Configuration Register
LM75B_REG_ADDR_HYSTERESIS = 0x02    # 
LM75B_REG_ADDR_OVERTEMP = 0x03      # 


class LM75B_TempSensor(object):
    def __init__(self, address=LM75B_DEV_ADDRESS, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.address = address
        self.debug = debug

        # Read configuration settings
        self.config = self._get_configuration()

    def _get_configuration(self):
        # Read from the temperature sensor Configuration Register
        return self.i2c.readS8(LM75B_REG_ADDR_CONFIG)

    def _set_configuration(self, new_config):
        """ Change the contents of the volatile configuration register

            7, 6, 5: Reserved
               4, 5: OS fault queue
                  2: OS polarity
                  1: OS operation mode
                  0: Shutdown
        """
        if self.config != new_config:
            # Read from the temperature sensor Temperature Register
            command = self.swap_bytes(new_config)
            try:
                self.i2c.write8(LM75B_REG_ADDR_CONFIG, command)
            except IOError:
                pass
            else:
                self.config = new_config

    def read_temperature(self):
        """ Return a temperature reading in degrees Centigrade """
        # Read from the temperature sensor Temperature Register
        reading = self.i2c.readS16(LM75B_REG_ADDR_TEMP, False)
        # Return the temperature reading in degC
        return (reading >> 5) / 8.0


    def set_shutdown_mode(self, enabled):
        """ Enable or disable device Shutdown mode.

        DESCRIPTION
        ===========
        The LM75B can be placed into a low-power state by enabling
        Shutdown mode. In this mode, the LM75B will not take any
        measurements but I2C and register access remains active.

        PARAMETERS
        ==========
        enabled: <bool>
            Set to 1 to enable Shutdown mode, or to 0 to disable
            Shutdown mode

        RETURNS
        =======
        Nothing.
        """
        # Copy the current configuration and clear bits to change
        config = self.config
        config &= ~(1 << 0)
        # Update the Shutdown bit and submit the new config
        if enabled:
            config |= (1 << 0)
        self._set_configuration(config)

    def _print(self, message):
        if self.debug is True:
            print message

    def swap_bytes(self, word):
        """
        Swap the LSB and MSB bytes of ``word`` around. Necessary for
        some I2C communication, depending on how the follower interprets
        data i.e. little endian or big endian
        """
        funny_word = ((word << 8) & 0xFF00) + (word >> 8)
        return funny_word
