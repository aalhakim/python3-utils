"""
Python driver module for the Atmel AT30TSE75xA 

(Feb 2017)
Product Page: http://www.atmel.com/devices/AT30TSE752A.aspx
Datasheet: http://www.atmel.com/Images/Atmel-8854-DTS-AT30TSE752A-754A-758A-Datasheet.pdf

TEMPERATURE
===========
Temperature is stored in a 16-bit Read-Only register. It is represented
in the twos complement format and can be configured to have a resolution
of 9-bits (0.5degC), 10-bits (0.25degC), 11-bits (0.125degC) or 12-bits
(0.0625degC) by setting the R1 and R0 bits on the configuration
register.

"""
########################################################################
import time
import sys
from adafruit_i2c import Adafruit_I2C


########################################################################
# I2C Follower Device addresses
AT30TSE75_DEV_ADDR_SENSOR = 0x48  # 0x49 in other cases?
AT30TSE75_DEV_ADDR_EEPROM = 0x50  # 0x51 in other cases?
AT30TSE75_DEV_ADDR_PROTECT = 0x31

# Temperature Sensor Register addresses
AT30TSE75_REG_ADDR_TEMP = 0x00  # 16-bit, read-only, 2s complement
AT30TSE75_REG_ADDR_CONFIG = 0x01
AT30TSE75_REG_ADDR_LIMIT_TLO = 0x02
AT30TSE75_REG_ADDR_LIMIT_THI = 0x03
# Non-volatile memory registers
AT30TSE75_REG_ADDR_NV_CONFIG = 0x11
AT30TSE75_REG_ADDR_NV_LIMIT_TLO = 0x12
AT30TSE75_REG_ADDR_NV_LIMIT_THI = 0x13


class AT30TSE75_TempSensor(object):
    def __init__(self, address=AT30TSE75_DEV_ADDR_SENSOR, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.address = address
        self.debug = debug

        # Read configuration settings
        self.config = self._get_configuration()

    def _get_configuration(self):
        # Read from the temperature sensor Configuration Register
        return self.i2c.readS16(AT30TSE75_REG_ADDR_CONFIG, False)

    def _set_configuration(self, new_config):
        """ Change the contents of the volatile configuration register
        """
        if self.config != new_config:
            # Read from the temperature sensor Temperature Register
            command = self.swap_bytes(new_config)
            try:
                self.i2c.write16(AT30TSE75_REG_ADDR_CONFIG, command)
            except IOError:
                pass
            else:
                self.config = new_config

    def _save_configuration(self):
        """ Copy the configuration register contents to the non-volatile
        configuration register

        See "Section 9.2: Copy Volatile Registers to Nonvolatile
        Registers" of datasheet (page 35).
        """
        # Send the copy contents from non-volatile to volatile Opcode
        self.i2c.write8(0x48, 0)

    def _load_configuration(self):
        """ Copy the non-volatile configuration register contents to the
        volatile configuration register

        See "Section 9.1: Copy Nonvolatile Registers to Volatile
        Registers" of datasheet (page 35).
        """
        # Update the device address to that of the temperature sensor
        self._address_temperature_sensor()
        # Send the copy contents from non-volatile to volatile Opcode
        self.i2c.write8(0xB8, 0)

    def read_temperature(self):
        """ Return a temperature reading in degrees Centigrade """
        # Read from the temperature sensor Temperature Register
        reading = self.i2c.readS16(AT30TSE75_REG_ADDR_TEMP, False)
        # Return the temperature reading in degC
        #   T: temperature (degC)
        #   x: register content (reading)
        #   r: resolution configuration [0, 1, 2, 3]
        #       T = x * (1 / POW(2, 7-r)) * (0.5 / POW(2, r))
        #       T = x * (1 / POW(2, 7-r+r+1))
        #       T = x * (1 / POW(2, 8))
        return reading / 256.0

    def trigger_one_shot(self):
        """ Trigger a one-shot temperature measurement.

        DESCRIPTION
        ===========
        One-Shot Temperature Measurement mode is only activated when the
        AT30TSE75xA is in Shutdown mode. If a 1 is sent when in Shutdown
        mode the AT30TSE75xA will wake-up up to perform a single
        measurement and conversion. Following this, the device will
        clear the One-Shot bit and then go back into Shutdown mode.

        This mode is intended for low-power consumption situations.

        PARAMETERS
        ==========
        Nothing.

        RETURNS
        =======
        Nothing.
        """
        # Copy the current configuration and clear bits to change
        config = self.config
        config &= ~(1 << 15)
        # Set the One-Shot bit and submit the new configuration
        config |= (1 << 15)
        self._set_configuration(config)

    def set_resolution(self, mode):
        """ Configure the resolution of the temperature sensor.

        DESCRIPTION
        ===========
        Change the resolution of the temperature readings. Higher
        resolutions have a longer delay between samples.
          -  9-bit: 0.5000 degC per LSB ("vlow")
          - 10-bit: 0.2500 degC per LSB ("low")
          - 11-bit: 0.1250 degC per LSB ("high")
          - 12-bit: 0.0625 degC per LSB ("vhigh")

        PARAMETERS
        ==========
        mode: <string>
            Should be a string "vlow", "low", "high", "vhigh" to
            indicate which resolution to use (see Description above)

        RETURNS
        =======
        Nothing.

        RAISES
        ======
        Nothing.
        """
        # Copy the current configuration and clear bits to change
        config = self.config
        config &= ~(0b11 << 13)

        # Identify the new configuration
        if mode == "vlow":
            #  9-bit, 0.5 degC, t_conv=25ms
            resolution = 0b00
        elif mode == "low":
            # 10-bit, 0.25 degC, t_conv=50ms
            resolution = 0b01
        elif mode == "high":
            # 11-bit, 0.125 degC, t_conv=100ms
            resolution = 0b10
        elif mode == "vhigh":
            # 12-bit, 0.0625 degC, t_conv=200ms
            resolution = 0b11
        else:
            self._print("ERROR: '{}' is not a valid resolution option")
            resolution = 0b00

        # Submit the new configuration
        config |= (resolution << 13)
        self._set_configuration(config)

    def set_fault_tolerance(self, mode):
        """ Configure the Fault Tolerance setting.

        DESCRIPTION
        ===========
        This is used to determine how many faults may occur before the
        AT30TSE75xA ALERT pin is activated.

        PARAMETERS
        ==========
        mode: <int>
            Set to 0b00 (0), 0b01 (1), 0b10 (2) or 0b11 (3) to define
            how many faults are allowed before the ALERT pin is
            activated.
              mode=0b00: 1 consecutive fault required
              mode=0b01: 2 consecutive faults required
              mode=0b10: 4 consecutive faults required
              mode=0b11: 6 consecutive faults required

        RETURNS
        =======
        Nothing.
        """
        # Copy the current configuration and clear bits to change
        config = self.config
        config &= ~(0b11 << 11)
        # Update the Fault Tolerance bits and submit the new config
        config |= (mode << 11)
        self._set_configuration(config)

    def set_shutdown_mode(self, enabled):
        """ Enable or disable device Shutdown mode.

        DESCRIPTION
        ===========
        The AT30TSE75xA can be placed into a low-power state by enabling
        Shutdown mode. In this mode, the AT30TSE75xA will not take any
        measurements unless the One-Shot bit is set.

        PARAMETERS
        ==========
        enabled: <bool>
            Set mode=1 to enable Shutdown mode, or mode=False to disable
            Shutdown mode (i.e. the AT30TSE75xA will take continuous
            measurements)

        RETURNS
        =======
        Nothing.
        """
        # Copy the current configuration and clear bits to change
        config = self.config
        config &= ~(1 << 8)
        # Update the Shutdown bit and submit the new config
        if enabled:
            config |= (1 << 8)
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


# Temperature Sensor Register addresses
WRITE_DELAY = 0.005  # seconds


class AT30TSE75_EEPROM(object):
    """ This class allows interaction with the serial EEPROM on the
    AT30TSE75xA devices, where x represents the number of kb of i
    integrated memory (2kb, 4kb, 8kb).

    Memory Organisation
    ===================
    The serial EEPROM is internally organised into pages, or rows of
    data bytes. Each page contains 16 bytes.
        AT30TSE752A: 16 pages of 16 bytes = 2 kilobits
        AT30TSE754A: 32 pages of 16 bytes = 4 kilobits
        AT30TSE758A: 64 pages of 16 bytes = 8 kilobits
    """
    def __init__(self, address=AT30TSE75_DEV_ADDR_EEPROM, debug=False):
        self.i2c = Adafruit_I2C(address=address, debug=debug)
        self.address = address
        self.debug = debug

    def _valid_byte_address(self, address):
        valid_address = True
        if address not in range(0, 256, 1):
            valid_address = False
        return valid_address

    def _valid_page_address(self, address):
        valid_address = True
        if address not in range(0, 256, 16):
            valid_address = False
        return valid_address

    def _valid_page_number(self, page_number):
        valid_number = True
        if page_number not in range(0, 16, 1):
            valid_number = False
        return valid_number

    def _write_byte_int(self, byte_address, data):
        # Validate the size of the data
        if data < -128 or data > 256:
            raise ValueError("'data={}' must be smaller than 1 byte".format(data))

        # Write to memory
        self.i2c.write8(byte_address, data)
        time.sleep(WRITE_DELAY)

    def _write_byte_str(self, byte_address, data):
        # Validate the size of the data
        bin_string = "".join("{:08b}".format(ord(x)) for x in str(data))
        if len(bin_string) > 8:
            raise ValueError("'data={}' must be smaller than 1 byte".format(data))
        
        # Write to memory
        data = int(bin_string, 2)
        self.i2c.write8(byte_address, data)
        time.sleep(WRITE_DELAY)


    def write_byte(self, byte_address, data):
        """ Write a byte of data to the byte address `byte_address`
        
        PARAMETERS
        ==========
        byte_address: <int>
            A integer address value between 0 (first location in memory)
            and 255 (last location) [for 2kb device].

        data: <str/+int, 8-bit>
            An 8-bit value of data to be stored in the desired memory
            location.

        RETURNS
        =======
        Nothing.

        RAISES
        ======
        ValueError: Invalid value- `data` is larger than 1 byte, or 
                    not a string or integer.
        TypeError: Invalid byte address in memory

        """
        # Validate the memory address
        if not self._valid_byte_address(byte_address):
            raise ValueError("'{}' is not a valid 8-bit byte-address ".format(byte_address))

        datatype = type(data)
        if datatype == str:
            self._write_byte_str(byte_address, data)
        elif datatype == int:
            self._write_byte_int(byte_address, data)
        else:
            raise TypeError("'data={}' should be <str> or <int>".format(data))

    def write_str_to_page(self, page_number, data):
        """ Write up to a page of data to a page

        DESCRIPTION
        ===========
        `data` can be any length although it should ideally be less than
        or equal to the length of a page (16 bytes). If data is greater
        than 16-bytes, then the AT30TSE75xA address counter will
        rollover to the start of the same page. That is, only one page
        can be written to in a single operation.
        
        PARAMETERS
        ==========
        data: <list of [str]>
            A list of ASCII characters, with a maximum length of 16.

        page_number: <int>
            The page number to write to as an integer multiple of 16 
            between 0 and 255 (because there are 16 pages available).
            Valid page addresses are:
            [
                  0,  16,  32,  48,  64,  80,  96, 112,
                128, 144, 160, 176, 192, 208, 224, 240
            ]
            Therefore, valid page numbers are:
            [
                 0,  1,  2,  3,  4,  5,  6, 7,
                 8,  9, 10, 11, 12, 13, 14, 15
            ]

        RETURNS
        =======
        Nothing.
        """
        # Validate the page_number
        if not self._valid_page_number(page_number):
            raise ValueError("'{}' is not a valid page number ".format(page_number))
        page_address = page_number * 16

        # Validate the memory address
        if not self._valid_page_address(page_address):
            raise ValueError(
                "'{}' is not a valid page-address. It should be a multiple of 16 from 0 to 240."
                .format(page_address)
                )

        # Check that data is a string
        data_type = type(data)
        if data_type != str:
            raise TypeError("'data={}' must be <str>".format(data))
        
        # Convert the character string to a list of bytes
        bin_string = " ".join("{:08b}".format(ord(x)) for x in str(data))
        bin_list = [int(byte, 2) for byte in bin_string.split(" ")]
                   
        # Check the number of bytes will fit within the available space
        if len(bin_list) > 16:
            raise IOError("'data={}' must be smaller than 16 bytes (1char=1byte)".format(data))

        # Write to EEPROM
        self.i2c.writeList(page_address, bin_list)
        time.sleep(WRITE_DELAY)

    def read_byte(self, byte_address):
        # Validate the memory address
        if not self._valid_byte_address(byte_address):
            raise TypeError("'0b{0:08b}' is not a valid 8-bit byte address ".format(byte_address))
        # Read the byte
        return self.i2c.readU8(byte_address)

    def read_page(self, page_number):
        # Validate the page_number
        if not self._valid_page_number(page_number):
            raise ValueError("'{}' is not a valid page number ".format(page_number))
        page_address = page_number * 16

        # Validate the memory address
        if not self._valid_byte_address(page_address):
            raise TypeError("'0b{0:08b}' is not a valid page address ".format(page_address))
        # Read the page data
        return self.i2c.readList(page_address, 16)

    def clear_page(self, page_number):
        # Validate the page_number
        if not self._valid_page_number(page_number):
            raise ValueError("'{}' is not a valid page number ".format(page_number))
        page_address = page_number * 16

        self.i2c.writeList(page_address, [0xFF]*16)
        time.sleep(WRITE_DELAY)

    def clear_memory(self):
        for page_address in range(0, 16):
            self.clear_page(page_address)

    def _print(self, message):
        if self.debug is True:
            print message
