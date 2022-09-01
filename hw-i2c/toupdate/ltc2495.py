
"""
Driver code for LTC2495 Data Aquisition I2C device.

https://www.analog.com/en/products/ltc2495.html#
"""

# Standard library imports
import time
import logging
debugLogger = logging.getLogger(__name__)


# >>--------- CONFGURE CONSOLE LOGGING FROM DIRECT EXECUTION ---------<<
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)7s | %(name)s.%(funcName)s: %(message)s',
        handlers=[logging.StreamHandler()])
# >>------------------------------------------------------------------<<

# Local library import
DEBUG_MODE = False

if DEBUG_MODE:
    from i2c_handler_mock import I2CHandler
else:
    from drivers.i2c_handler import I2CHandler


########################################################################
LTC2495_DEFAULT_ADDRESS = 0x76

# The number of expected bytes in a read command
READ_BLOCK_LENGTH = 3  # bytes


########################################################################
# Configuration bits in the channel select control register.
# Allowed bit shift range is 0 (LSB) to 7 (MSB)
BIT_PREAMBLE = (1 << 7)
BIT_EN  = (1 << 5)
BIT_SGL = (1 << 4)
BIT_ODD = (1 << 3)
BIT_A2  = (1 << 2)
BIT_A1  = (1 << 1)
BIT_A0  = (1 << 0)
# Other bits are either unused.

# Configuration bits in the mode select control register.
# Allowed bit shift range is 0 (LSB) to 7 (MSB)
BIT_EN2 = (1 << 7)
BIT_IM  = (1 << 6)
BIT_FA  = (1 << 5)
BIT_FB  = (1 << 4)
BIT_SPD = (1 << 3)
BIT_GS2 = (1 << 2)
BIT_GS1 = (1 << 1)
BIT_GS0 = (1 << 0)

GAIN_SELECTION = {
    '1x': {1: 0x0, 4: 0x1, 8: 0x2, 16: 0x3, 32: 0x4, 64: 0x5, 128: 0x6, 256: 0x7},
    '2x': {1: 0x0, 2: 0x1, 4: 0x2,  8: 0x3, 16: 0x4, 32: 0x5,  64: 0x6, 128: 0x7}
}


########################################################################
class LTC2495_16ChannelADC(object):

    def __init__(self, i2c, address=LTC2495_DEFAULT_ADDRESS, debug=False):
        self._i2c = i2c
        self.address = address
        self.debug = debug

        self.reg_config_channel = 0x80
        self.reg_config_mode = 0x00

        self.temperature_mode = False
        self.active_channel = None
        self.speed_mode = '1x'

    def i2c(self):
        """ Configure target address of the I2C Handler if not correct.
        """
        if self._i2c.address != self.address:
            self._i2c.set_address(self.address)

        return self._i2c

    def read_temperature(self, reset=False):
        """ Return a measurement from the internal temperature monitor.

        If temperature mode is not yet active, it will be configured.
        If temperature mode is already active, it will not be configured.

        If reset is True, the configuration will return to external
        conversion mode after the temperature conversion is obtained.
        """
        reset_temp_mode = self.temperature_mode

        # If temperature mode is off, turn it on.
        if self.temperature_mode is False:
            self._config_measure_temperature(True)
            self.set_mode()

        result = self.i2c().readBlock(READ_BLOCK_LENGTH)

        # Return temperature mode to the original setting if `reset` is
        # True.
        if reset is True and self.temperature_mode != reset_temp_mode:
            self._config_measure_temperature(reset_temp_mode)
            self.set_mode()

        return result

    def read_channel(self, channel):
        """ Obtain a measurement from an external channel.
        """
        assert(channel >= 0 and channel <= 15)

        # If temperature mode is on, turn it off.
        if self.temperature_mode is True:
            self._config_measure_temperature(True)
            self.set_mode()

        # Change the channel if `channel` is not already selected.
        if self.active_channel != channel:
            self.set_channel(channel)

        self.i2c().readBlock(READ_BLOCK_LENGTH)

    def set_channel(self, channel):
        """ Select a new channel.
        """
        assert(channel >= 0 and channel <= 15)

        self._configure_channel(BIT_PREAMBLE, True)
        self._configure_channel(BIT_EN, True)
        self._config_single_ended(channel)

        if self.debug is True:
            debugLogger.info('Channel {:>2d}: 0b{:08b}'.format(channel, self.reg_config_channel))

        self.i2c().writeByte(self.reg_config_channel)


    def set_mode(self, channel=None, temp_mode=None, rejection_mode=None, speed_mode=None, gain=None):
        """ Update all configuration settings.
        """
        assert(channel >= 0 and channel <= 15)

        # Determine whether a channel should be selected or not.
        self._configure_channel(BIT_PREAMBLE, True)
        if channel is not None:
            self._configure_channel(BIT_EN, True)
            self._config_single_ended(channel)
        else:
            self._configure_channel(BIT_EN, False)

        # Define new configuration settings, if given.
        self._config_enable_mode_change(True)
        if temp_mode is not None:
            self._config_measure_temperature(temp_mode)

        if rejection_mode is not None:
            self._config_rejection_mode(rejection_mode)

        if speed_mode is not None:
            self._config_speed_mode(speed_mode)
        else:
            speed_mode = self.speed_mode

        if gain is not None:
            self._config_gain(gain, speed_mode)

        # Assuming a little-endian operation i.e. LSByte goes first.
        msbyte = 0xFF00 & (self.reg_config_mode << 8)
        lsbyte = self.reg_config_channel
        self.i2c().writeWord(msbyte | lsbyte)

    #-------------------------------------------------------------------
    def _config_single_ended(self, channel):
        """

        Args
        ====
        channel: <integer>
            Select a channel number from 0 to 15.
        """
        is_odd = (channel % 2) == 1

        self._configure_channel(BIT_SGL, True)
        self._configure_channel(BIT_ODD, is_odd)

        if is_odd:
            channel_select = int((channel - 1) / 2)
        else:
            channel_select = int(channel / 2)

        control_bits = BIT_A2 | BIT_A1 | BIT_A0
        self._configure_channel(control_bits, channel_select)

    #-------------------------------------------------------------------
    def _config_enable_mode_change(self, state):
        """ Set the EN2 configuration
        """
        assert(state == True or state == False)
        self._configure_mode(BIT_EN2, state)

    def _config_measure_temperature(self, state):
        """ Perform a measurement on the internal temperature monitor.

        Enabling this bit will command the next conversation cycle to
        sample from the internal temperature monitor instead of from
        the selected external ADC channel.
        """
        assert(state == True or state == False)
        self.temperature_mode = state
        self._configure_mode(BIT_IM, state)

    def _config_rejection_mode(self, mode):
        """ Select line frequency noise rejeciton mode.

        Args
        ====
        mode: <string>
            '50hz': Reject 50 Hz noise better than 110 dB.
            '60hz': Reject 60 Hz noise better than 110 dB.
            'both': Reject 50 Hz and 60 Hz noise by at least 87 dB.
        """
        mode = mode.lower()
        if mode == 'both':
            state = 0
        elif mode == '50hz':
            state = BIT_FB
        elif mode == '60hz':
            state = BIT_FA
        else:
            raise RuntimeError('Invalid mode chosen for rejection frequency configurtation: {}'.format(mode))

        control_bits = BIT_FA | BIT_FB
        self._configure_mode(control_bits, state)

    def _config_speed_mode(self, mode):
        """ Select 1x or 2x conversion speed, with some caveats.

        The default speed setting is 1x which makes two conversions
        per conversion cycle. This method produces a reading free from
        offset and drift. This can be changed to only have one conversion
        per conversion cycle but may result in a reading with some error.

        Args
        ====
        mode: <string>
            '1x': Set the speed mode to 1x (2 conversions per cycle, no error)
            '2x': Set the speed mode to 2x (1 conversion per cycle, with error)
        """
        mode = mode.lower()
        if mode == '1x':
            state = 0
        elif mode == '2x':
            state = 1
        else:
            raise RuntimeError('Invalid mode chosen for rejection frequency configurtation: {}'.format(mode))

        self.speed_mode = mode
        self._configure_mode(BIT_SPD, state)

    def _config_gain(self, gain, speed_mode):
        """ Set the gain value to use.

        Args
        ====
        gain: <integer>
            Set the gain value from the following group of valid inputs:
                1, 2, 4, 8, 16, 32, 64, 128, 256
            The range [1, 4, 8, 16, 32, 64, 128, 256] is valid for speed mode 1x
            The range [1, 2, 4,  8, 16, 32,  64, 128] is valid for speed mode 2x

        speed_mode: <string>
            Should be '1x' or '2x'. See self._config_speed_mode for a
            description of what these settings do. For this method, the
            speed mode relates to what gain levels are valid.
        """
        if gain not in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
            raise RuntimeError('Invalid gain of {} selected.'.format(gain))
        elif gain == 2 and speed_mode == '1x':
            raise RuntimeError('Invalid gain of {} selected for speed mode "1x".'.format(gain))
        elif gain == 256 and speed_mode == '2x':
            raise RuntimeError('Invalid gain of {} selected for speed mode "2x".'.format(gain))

        state = GAIN_SELECTION[speed_mode][gain]

        control_bits = BIT_GS2 | BIT_GS1 | BIT_GS0
        self._configure_mode(control_bits, state)

    #-------------------------------------------------------------------
    def _configure_channel(self, control_bits, state):
        """ Set the bit to the value of state.

        Args
        ====
        control_bits: <int> 8-bits
            A binary number where only the bits of interest are high
            and all other bits are low. e.g. 0b00010000

        state: <boolean> or <int> 8-bits
            Set to True to set the desired control bit to high, else
            False to set the desired control bit low, in the
            register_config.

            Use an integer 8-bit value to set/clear multiple bits
            simultaneously
        """
        if state is True:
            self.reg_config_channel |= control_bits
        elif state is False:
            self.reg_config_channel &= ~(control_bits)
        else:
            self.reg_config_channel &= ~(control_bits)
            self.reg_config_channel |= state

    def _configure_mode(self, control_bits, state):
        """ Set the bit to the value of state.

        Args
        ====
        control_bits: <int> 8-bits
            A binary number where only the bits of interest are high
            and all other bits are low. e.g. 0b00010000

        state: <boolean>
            Set to True to set the desired control bit to high, else
            False to set the desired control bit low, in the
            register_config.
        """
        if state:
            self.reg_config_mode |= control_bits
        else:
            self.reg_config_mode &= ~(control_bits)


########################################################################

if __name__ == "__main__":

    i2c = I2CHandler(address=LTC2495_DEFAULT_ADDRESS)
    device = LTC2495_16ChannelADC(i2c, debug=False)
    for i in range(16):
        device.set_channel(i)
